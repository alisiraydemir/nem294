#pip install pyXSteam
#pip install pandas


from pyXSteam.XSteam import XSteam
import math

steamTable = XSteam(XSteam.UNIT_SYSTEM_MKS)

class SteamSystem:
    def __init__(self, P_atm, T_operate, Area, Volume, Kg_Water, F_Qualtiy, Source_Q,Lid_Radius):
        self.P_atm = P_atm  # Atmospheric pressure in kPa
        self.T_operate = T_operate  # Operating temperature in °C
        self.Area = Area  # Surface area in m^2
        self.Volume = Volume  # Volume in m^3
        self.Kg_Water = Kg_Water  # Mass of water in kg
        self.F_Quality = F_Qualtiy # No unit
        self.Source_Q = Source_Q # Source in Kw
        self.Lid_Radius = Lid_Radius # Lid_Radius in m
        # Calculate P_initial using XSteam
        self.P_initial = steamTable.psat_t(self.T_operate)*100  # Saturation pressure in kPa

    def calculate_petcock_mass(self):
        m_of_petcock = (self.Area * (self.P_initial - self.P_atm) / 9.81)*1000
        return m_of_petcock
    def calculate_mass_lid(self):
        area = math.pi * math.pow(self.Lid_Radius, 2)
        m_of_lid = area*(self.P_initial - self.P_atm)*1000 / 9.81
        return m_of_lid
    def calculate_heat_transfer(self):
        volume_1 = self.Volume / self.Kg_Water
        vf = steamTable.vL_t(self.T_operate)
        vg = steamTable.vV_t(self.T_operate)
        vfg = vg - vf
        volume_2 = vf + (self.F_Quality*vfg)
        quality_1 = (volume_1 - vf) / vfg
        # Instead of Uf I calculated u_1. But it doesn't make significant difference.
        u_1 = steamTable.uL_t(self.T_operate) + quality_1*(steamTable.uV_t(self.T_operate))
        u_2 = steamTable.uL_t(self.T_operate) + self.F_Quality*(steamTable.uV_t(self.T_operate))
        m_1 = self.Kg_Water
        m_2 = self.Volume / volume_2
        m_e = m_1 - m_2
        h_e = steamTable.hV_t(self.T_operate)
        heat_transfer = (m_e*h_e) + (m_2*u_2) - (m_1*u_1)


        """print("Volume 1:", volume_1)
        print("vf:", vf)
        print("vg:", vg)
        print("vfg:", vfg)
        print("volume_2:", volume_2)
        print("quality_1:", quality_1)
        print("u_1:", u_1)
        print("u_2:", u_2)
        print("m_1:", m_1)
        print("m_2:", m_2)
        print("m_e:", m_e)
        print("h_e:", h_e)"""
        return heat_transfer
    def length_of_the_cooking_period(self):
        heat_transfer = self.calculate_heat_transfer()
        time = (heat_transfer / self.Source_Q)/3600  # In hour.
        return time


import pandas as pd
pd.set_option('display.max_columns', 12)
df = pd.DataFrame(columns=["t_operate(celcius)", "petcock_mass(kg)", "heat_transfer(kJ)", "time_period(h)", "lid_mass(kg)"])

for T in range(120, 165, 5):
    steam_system = SteamSystem(P_atm=100, T_operate=T, Area=4.8e-6, Volume=0.006, Kg_Water=3, F_Qualtiy=0.006,
                               Source_Q=2, Lid_Radius=0.125)
    petcock_mass = steam_system.calculate_petcock_mass()
    heat_transfer = steam_system.calculate_heat_transfer()
    time_period = steam_system.length_of_the_cooking_period()
    lid_mass = steam_system.calculate_mass_lid()

    new_row = {"t_operate(celcius)": T, "petcock_mass(kg)": petcock_mass, "heat_transfer(kJ)": heat_transfer,
               "time_period(h)": time_period, "lid_mass(kg)": lid_mass}
    df = pd.concat([df, pd.DataFrame(new_row, index=[0])], ignore_index=True)


print(df)

