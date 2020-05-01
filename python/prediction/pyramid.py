import numpy as np
import pandas as pd
from period_of_life import periodOfLife
class pyramid:
    def __init__(self):
        # SOURCE: https://www.populationpyramid.net/
        self._age_bins = [
            "0-4", "5-9", "10-14", "15-19", "20-24", "25-29",
            "30-34", "35-39", "40-44", "45-49", "50-54", "55-59",
            "60-64", "65-69", "70-74", "75-79", "80-84", "85-89",
            "90-94", "95-99", "100+"
        ]
        self._pyramid_df = pd.DataFrame({"Age_bin": self. _age_bins})

        # Global (WORLD)
        _name = "Global"
        _male = [
            349432556,
            342927576,
            331497486,
            316642222,
            308286775,
            306059387,
            309236984,
            276447037,
            249389688,
            241232876,
            222609691,
            192215395,
            157180267,
            128939392,
            87185982,
            54754941,
            33648953,
            15756942,
            5327866,
            1077791,
            124144
        ]
        _female = [
            328509234,
            321511867,
            309769906,
            295553758,
            289100903,
            288632766,
            296293748,
            268371754,
            244399176,
            238133281,
            223162982,
            195633743,
            164961323,
            140704320,
            101491347,
            69026831,
            48281201,
            26429329,
            11352182,
            3055845,
            449279
        ]
        self._pyramid_df[_name] = np.array(_male) + np.array(_female)

        _name = "China"
        _male = [
            44456332,
            46320144,
            45349923,
            44103122,
            46273865,
            51522843,
            66443228,
            51345507,
            49289359,
            61173349,
            62348020,
            49958045,
            38917285,
            36526788,
            21425163,
            12207276,
            6883629,
            2843084,
            731228,
            116377,
            12773
        ]
        _female = [
            39476105,
            40415039,
            38912828,
            38238737,
            40884302,
            46466160,
            62295742,
            48745948,
            46984787,
            58664268,
            61097362,
            48782446,
            38596854,
            37622978,
            23524526,
            14337340,
            9297788,
            4738693,
            1573796,
            358816,
            61919
        ]
        self._pyramid_df[_name] = np.array(_male) + np.array(_female)

        _name = "Japan"
        _male = [
            2453834,
            2773482,
            2856888,
            2926787,
            3075580,
            3151556,
            3475526,
            3918085,
            4307199,
            5088697,
            4364792,
            3964557,
            3733454,
            4095950,
            4312462,
            3160764,
            2209841,
            1282793,
            495632,
            95394,
            9772
        ]
        _female = [
            2324647,
            2628006,
            2707638,
            2775858,
            2921297,
            2998892,
            3314219,
            3747586,
            4161221,
            4915957,
            4293819,
            3918347,
            3762668,
            4283163,
            4814856,
            3897293,
            3129208,
            2347551,
            1290191,
            422131,
            68864
        ]
        self._pyramid_df[_name] = np.array(_male) + np.array(_female)

        _name = "Italy"
        _male = [
            1197289,
            1374731,
            1470174,
            1484455,
            1526577,
            1625230,
            1702976,
            1824273,
            2092329,
            2401070,
            2420466,
            2274884,
            1903045,
            1679600,
            1586760,
            1182323,
            958360,
            504059,
            186608,
            39461,
            3055
        ]
        _female = [
            1127405,
            1295570,
            1387183,
            1391636,
            1415929,
            1535700,
            1662536,
            1808649,
            2096655,
            2431950,
            2487780,
            2384062,
            2050522,
            1851695,
            1805038,
            1454787,
            1344033,
            893202,
            453131,
            133178,
            13462
        ]
        self._pyramid_df[_name] = np.array(_male) + np.array(_female)

        # South Korea (Republic of Korea)
        _name = "South Korea"
        _male = [
            974300,
            1158751,
            1174844,
            1289269,
            1683129,
            1870859,
            1733487,
            1974613,
            2015813,
            2186422,
            2168485,
            2082574,
            1855904,
            1287861,
            929821,
            664900,
            403886,
            160921,
            41739,
            7689,
            587
        ]
        _female = [
            922711,
            1098051,
            1101938,
            1187207,
            1533115,
            1629191,
            1548938,
            1822801,
            1909121,
            2107488,
            2147031,
            2078609,
            1918662,
            1391279,
            1068270,
            897655,
            679943,
            379182,
            143170,
            35207,
            3760
        ]
        self._pyramid_df[_name] = np.array(_male) + np.array(_female)

        _name = "Iran"
        _male = [
            3913297,
            3566704,
            3185825,
            2829745,
            2801162,
            3382446,
            4211840,
            4120404,
            3270956,
            2608048,
            2321587,
            1826123,
            1559797,
            1128726,
            709933,
            471441,
            306847,
            162121,
            27495,
            3670,
            238
        ]
        _female = [
            3724262,
            3361593,
            3032120,
            2700238,
            2755066,
            3404233,
            4254862,
            4152339,
            3220365,
            2556247,
            2296892,
            1850729,
            1572477,
            1135905,
            738068,
            435165,
            244765,
            115360,
            29181,
            4400,
            280
        ]
        self._pyramid_df[_name] = np.array(_male) + np.array(_female)

        _name = "UK"
        _male = [
            2009363,
            2108550,
            2022370,
            1880611,
            2072674,
            2275138,
            2361054,
            2279836,
            2148253,
            2128343,
            2281421,
            2232388,
            1919839,
            1647391,
            1624635,
            1137438,
            766956,
            438663,
            169952,
            34524,
            3016
        ]
        _female = [
            1915127,
            2011016,
            1933970,
            1805522,
            2001966,
            2208929,
            2345774,
            2308360,
            2159877,
            2167778,
            2353119,
            2306537,
            1985177,
            1734370,
            1763853,
            1304709,
            969611,
            638892,
            320625,
            95559,
            12818
        ]
        self._pyramid_df[_name] = np.array(_male) + np.array(_female)

        _name = "US"
        _male = [
            10055063,
            10246393,
            10777513,
            10834321,
            11322732,
            12144455,
            11702514,
            10858871,
            10118582,
            9969099,
            10319535,
            10702065,
            10049886,
            8465274,
            6645519,
            4326986,
            2805623,
            1538659,
            703131,
            179003,
            20792
        ]
        _female = [
            9621269,
            9798759,
            10311974,
            10408587,
            10936013,
            11690875,
            11349965,
            10756920,
            10176017,
            10084699,
            10258272,
            10840205,
            10619257,
            9353753,
            7709344,
            5400748,
            3655579,
            2372445,
            1348005,
            447633,
            76312
        ]
        self._pyramid_df[_name] = np.array(_male) + np.array(_female)

        _name = "Australia"
        _male = [
            849691,
            833875,
            809143,
            767904,
            820079,
            914654,
            934339,
            897596,
            803525,
            825466,
            766933,
            762569,
            679944,
            593932,
            509764,
            347087,
            231870,
            132577,
            55712,
            13809,
            842
        ]
        _female = [
            805166,
            791506,
            768625,
            733706,
            788473,
            878319,
            932747,
            897661,
            812678,
            840928,
            785997,
            778154,
            710836,
            620305,
            535305,
            376503,
            272568,
            188213,
            98707,
            32256,
            3236
        ]
        self._pyramid_df[_name] = np.array(_male) + np.array(_female)

        _name = "India"
        _male = [
            61228414,
            61877169,
            66302628,
            66670854,
            64865811,
            62039339,
            58874888,
            53993918,
            46631243,
            40756605,
            35202663,
            30150272,
            24694672,
            19168129,
            11627908,
            7062999,
            3831463,
            1575584,
            437188,
            91981,
            17241
        ]

        _female = [
            55651093,
            56104958,
            59853324,
            59374711,
            57638993,
            55357930,
            53301210,
            49466260,
            43588651,
            38683675,
            33673299,
            29105996,
            24195856,
            19092154,
            12463535,
            8020956,
            4657548,
            1955555,
            555797,
            131216,
            30698
        ]

        self._pyramid_df[_name] = np.array(_male) + np.array(_female)

        _name = "Spain"
        _male = [
            1018775,
            1122860,
            1286746,
            1177739,
            1151526,
            1194797,
            1280330,
            1558391,
            1972854,
            2033122,
            1857275,
            1709577,
            1470410,
            1175573,
            1027554,
            826090,
            541682,
            372936,
            164949,
            33214,
            2701
        ]

        _female = [
            956261,
            1057033,
            1203904,
            1110412,
            1096729,
            1144986,
            1259748,
            1571064,
            1935544,
            1947657,
            1820863,
            1748824,
            1559667,
            1284147,
            1186037,
            1028502,
            761842,
            641233,
            347229,
            93129,
            11299
        ]

        self._pyramid_df[_name] = np.array(_male) + np.array(_female)

        _name = "France"
        _male = [
            1823505,
            1980578,
            2045337,
            1995493,
            1881326,
            1819520,
            1915487,
            2000778,
            1934827,
            2131742,
            2150181,
            2087715,
            1916803,
            1779687,
            1663921,
            1055012,
            733599,
            482262,
            211624,
            49824,
            3365
        ]

        _female = [
            1742250,
            1898341,
            1954448,
            1914108,
            1839115,
            1843203,
            1990482,
            2083933,
            1997689,
            2178751,
            2219374,
            2200132,
            2084324,
            2000775,
            1944915,
            1304258,
            1047708,
            845906,
            488137,
            167556,
            18186
        ]

        self._pyramid_df[_name] = np.array(_male) + np.array(_female)

        self._pyramid_df["Except China"] = self._pyramid_df["Global"] - self._pyramid_df["China"]

        df = self._pyramid_df.drop(["Age_bin"], axis=1).sum(axis=0)
        self.population_dict = df.to_dict()

    def get_population_dict(self):
        return self.population_dict

    def get_pyramid(self):
        return self._pyramid_df

    def get_pyramid_for(self, name):
        return self._pyramid_df[name]

    def add_to_pyramid(self,name, male, female):
        self._pyramid_df[name] = np.array(male) + np.array(female)

    def get_smoothed(self):
        df = self._pyramid_df.copy()
        series = df["Age_bin"].str.replace("+", "-122")
        df[["Age_first", "Age_last"]] = series.str.split("-", expand=True).astype(np.int64)
        df = df.drop("Age_bin", axis=1)
        series = df["Age_last"]
        df = df.apply(lambda x: x[:-2] / (x[-1] - x[-2] + 1), axis=1)
        df["Age"] = series
        df = pd.merge(df, pd.DataFrame({"Age": np.arange(0, 123, 1)}), on="Age", how="right", sort=True)
        df = df.fillna(method="bfill").astype(np.int64)
        df = df.set_index("Age")
        return df.copy()

    def life_out(self):
        pyramid_df = self.get_smoothed()
        pol = periodOfLife()
        _out_df = pol.get_life_outside()
        df = pyramid_df.cumsum()
        countries = df.columns[:]
        df = pd.merge(_out_df, df, left_on="Age_last", right_on="Age", how="left")
        _first = df.loc[df.index[0], countries]
        df[countries] = df[countries].diff()
        df.loc[df.index[0], countries] = _first
        df[countries] = df[countries].apply(lambda x: x / x.sum(), axis=0)
        out_df = df.copy()
        return out_df

    def weight_average_out(self,country):
        out_df = self.life_out()
        df = out_df.copy()
        df["Portion"] = df[country]
        ec_out_df = df.drop(self.population_dict.keys(), axis=1)
        ec_out_df["Weighted"] = (ec_out_df[["School", "Office", "Others"]].sum(axis=1) * ec_out_df["Portion"])
        return ec_out_df.copy()

    def weight_average_lockdown(self,country):
        ec_out_df = self.weight_average_out(country)
        df = ec_out_df.copy()
        df["School_Lockdown"] = 0
        df["Office_lockdown"] = 0
        df["Others_lockdown"] = 0

        df.loc[df.index[1:3], "Others_lockdown"] += 0.25
        df.loc[df.index[3:6], "Others_lockdown"] += 1
        df.loc[df.index[6:10], "Others_lockdown"] += 1
        df.loc[df.index[10:11], "Others_lockdown"] += 0.25

        df["Weighted_lockdown"] = (df[["School_Lockdown", "Office_lockdown", "Others_lockdown"]].sum(axis=1) * df["Portion"])

        return df.copy()



