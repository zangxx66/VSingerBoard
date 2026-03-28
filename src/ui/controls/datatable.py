import flet_datatable2 as ftd
from dataclasses import field
from flet import control


# 0.83.0 breaking change 临时解决方案
@control
class DataTable(ftd.DataTable2):
    data_row_max_height: None = field(default=100, init=False, repr=False, compare=False, metadata={"skip": True})
    data_row_min_height: None = field(default=1, init=False, repr=False, compare=False, metadata={"skip": True})
