from enum import Enum


class Exchange(str, Enum):
    NSE = "NSE"
    BSE = "BSE"
    AMFI = "AMFI"
    MCX = "MCX"