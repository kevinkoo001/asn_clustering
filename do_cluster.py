import logging
import draw_graph
import itertools
import util

try:
    import networkx as nx
    import numpy as np
    import matplotlib.pyplot as plt
    from sklearn.feature_extraction import image
    from sklearn.cluster import spectral_clustering
    from sklearn import cluster, datasets
    from sklearn.neighbors import kneighbors_graph
    from sklearn.preprocessing import StandardScaler
    
except importError:
    logging.error('Required library: networkx, numpy, matplot, sklearn')

'''
    Each metric is calculated by both networkx and gephi library.
    10 metrics have been selected when having high correlation coefficient (i.e., abs(corrcoef) > .25)
        between metric and three public indexes:
        FHI (free house index), DI(democracy index), and RWBI(reporters without borders index)
            [cc, fhi, di, rwbi, n_foreign_asns, n_asns_out_conn, average_shortest_path_length, diameter,
            radius, density, average degree, average path length, modularity, community number]
'''
dataset = [
        ['AE', 0.287356322, 0.176271186, 0.622317042, 112, 6, 2.650472335, 6, 3, 0.075573549, 2.769230769, 2.780026991, 0.39, 5],
        ['AF', 0.264367816, 0.190960452, 0.613136799, 1, 1, 1.981060606, 3, 2, 0.068181818, 2.181818182, 1.981060606, 0.191, 2],
        ['AL', 0.528735632, 0.518644068, 0.725239204, 4, 2, 2.846153846, 6, 3, 0.074224022, 2.820512821, 2.846153846, 0.455, 4],
        ['AM', 0.367816092, 0.344632768, 0.729635376, 69, 6, 2.631372549, 5, 3, 0.076862745, 3.058823529, 2.928627451, 0.449, 5],
        ['AO', 0.344827586, 0.256497175, 0.607964831, 12, 2, 2.661375661, 5, 3, 0.092592593, 2.387096774, 2.650918635, 0.485, 5],
        ['AR', 0.540229885, 0.650847458, 0.75963279, 63, 23, 2.926345609, 5, 3, 0.010979338, 3.707865169, 3.016436734, 0.476, 9],
        ['AT', 0.873563218, 0.842937853, 0.956943367, 1408, 53, 2.859310777, 6, 3, 0.011491228, 4.37593985, 2.908401657, 0.437, 12],
        ['AU', 0.873563218, 0.896045198, 0.877036462, 1065, 84, 3.025646682, 8, 4, 0.004608288, 5.136200717, 3.024866194, 0.391, 16],
        ['AZ', 0.195402299, 0.197740113, 0.34199638, 35, 2, 2.344444444, 5, 3, 0.065079365, 2.222222222, 2.398412698, 0.355, 4],
        ['BD', 0.517241379, 0.531073446, 0.54189294, 10, 11, 3.542164939, 7, 4, 0.016431925, 3.302325581, 3.640772399, 0.541, 9],
        ['BE', 0.988505747, 0.774011299, 0.942332558, 168, 31, 5.400549451, 17, 9, 0.022527473, 2.188976378, 5.368010167, 0.721, 14],
        ['BG', 0.701149425, 0.638418079, 0.671709335, 115, 48, 3.310233683, 7, 4, 0.006607575, 3.360623782, 3.310215953, 0.56, 12],
        ['BH', 0.149425287, 0.202259887, 0.338376002, 15, 4, 3.241830065, 7, 4, 0.124183007, 2.111111111, 3.241830065, 0.503, 4],
        ['BJ', 0.724137931, 0.516384181, 0.719162141, 2, 2, 1.333333333, 2, 1, 0.666666667, 1.333333333, 1.333333333, 0, 1],
        ['BR', 0.609195402, 0.711864407, 0.684380657, 323, 133, 3.2346754, 7, 1, 0.003713889, 11.16395078, 3.2346754, 0.281, 18],
        ['BT', 0.448275862, 0.428248588, 0.675071115, 22, 1, 1.8, 3, 2, 0.4, 1.6, 1.8, 0.219, 2],
        ['BW', 0.655172414, 0.767231638, 0.801008534, 11, 2, 2.076923077, 4, 2, 0.166666667, 2, 2.076923077, 0.275, 3],
        ['BY', 0.045977011, 0.294915254, 0.476855443, 27, 4, 2.681635926, 6, 3, 0.036888532, 2.390804598, 2.839347768, 0.555, 7],
        ['CA', 0.896551724, 0.903954802, 0.955133178, 1094, 129, 3.215616911, 9, 5, 0.004588983, 4.232606438, 3.303998916, 0.528, 19],
        ['CH', 0.977011494, 0.905084746, 0.918153607, 1845, 60, 2.876148724, 7, 4, 0.012697003, 5.355140187, 2.876201312, 0.367, 12],
        ['CI', 0.310344828, 0.276836158, 0.703516938, 6, 2, 2.133333333, 4, 2, 0.333333333, 1.666666667, 2.133333333, 0.3, 2],
        ['CL', 0.75862069, 0.759322034, 0.799844841, 28, 12, 2.968291251, 6, 4, 0.026423958, 3.435114504, 2.968291251, 0.484, 7],
        ['CM', 0.333333333, 0.263276836, 0.584820274, 4, 3, 1.75, 2, 1, 0.25, 1.75, 1.75, 0, 1],
        ['CN', 0.137931034, 0.216949153, 0.146237393, 274, 30, 3.215144336, 7, 4, 0.012664151, 3.19245283, 3.289490746, 0.607, 11],
        ['CO', 0.482758621, 0.618079096, 0.59193173, 30, 9, 3.150905433, 5, 3, 0.035814889, 2.405405405, 3.223874598, 0.625, 7],
        ['CR', 0.896551724, 0.785310734, 0.93871218, 10, 5, 2.922689076, 7, 4, 0.065546218, 2.1, 2.911519199, 0.606, 6],
        ['CY', 0.862068966, 0.714124294, 0.883630721, 85, 7, 2.719230769, 6, 4, 0.076923077, 2.904761905, 2.717029449, 0.417, 6],
        ['CZ', 0.896551724, 0.775141243, 0.946987329, 1138, 52, 3.385008069, 8, 4, 0.009847512, 3.426934097, 3.385008069, 0.526, 16],
        ['DE', 0.91954023, 0.854237288, 0.948926817, 2281, 214, 3.177459821, 8, 1, 0.004313232, 5.438985737, 3.177459821, 0.414, 28],
        ['DK', 0.977011494, 0.907344633, 0.990690458, 420, 19, 3.022355361, 6, 3, 0.01363677, 2.859813084, 3.022264944, 0.551, 11],
        ['DO', 0.643678161, 0.631638418, 0.744116886, 1, 1, 3.104761905, 7, 4, 0.152380952, 2.133333333, 3.104761905, 0.436, 4],
        ['DZ', 0.402298851, 0.310734463, 0.623610034, 1, 1, 1.5, 2, 1, 0.5, 1.333333333, 1.428571429, 0.375, 2],
        ['EC', 0.448275862, 0.541242938, 0.662141195, 1, 1, 2.910588235, 5, 3, 0.059607843, 2.862745098, 2.941176471, 0.494, 5],
        ['EE', 0.908045977, 0.752542373, 0.952547194, 95, 12, 2.387844612, 4, 2, 0.05764411, 2.440677966, 2.780946209, 0.453, 5],
        ['EG', 0.459770115, 0.235028249, 0.448538919, 42, 6, 2.40627451, 4, 2, 0.069019608, 3.450980392, 2.40627451, 0.322, 4],
        ['ES', 0.83908046, 0.787570621, 0.839281096, 266, 31, 3.974085106, 10, 5, 0.006851064, 2.619385343, 3.861987265, 0.67, 19],
        ['FI', 1, 0.898305085, 1, 508, 11, 3.294237813, 7, 4, 0.015567766, 2.548571429, 3.297133601, 0.601, 12],
        ['FJ', 0.448275862, 0.511864407, 0.692785105, 1, 1, 1, 1, 1, 1, 1, 1, 0.5, 2],
        ['FR', 0.83908046, 0.786440678, 0.823765193, 771, 162, 3.051645902, 8, 4, 0.006219401, 3.122629583, 3.268625521, 0.579, 22],
        ['GB', 0.873563218, 0.816949153, 0.8386346, 3608, 256, 3.247911571, 9, 1, 0.006953749, 8.560064935, 3.247911571, 0.304, 30],
        ['GE', 0.517241379, 0.53559322, 0.739074218, 14, 2, 2.80952381, 6, 3, 0.046365915, 2.542372881, 2.808390733, 0.458, 5],
        ['GH', 0.793103448, 0.593220339, 0.89681924, 16, 4, 1.980392157, 3, 2, 0.117647059, 1.875, 1.95212766, 0.579, 5],
        ['GM', 0.183908046, 0.22259887, 0.521851565, 1, 1, 1.5, 2, 1, 0.5, 1, 1, 0, 1],
        ['GQ', 0.068965517, 0.065536723, 0.240884407, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
        ['GR', 0.770114943, 0.719774011, 0.696276183, 98, 12, 3.433818589, 9, 5, 0.028219485, 2.526315789, 3.37704918, 0.589, 8],
        ['GT', 0.425287356, 0.534463277, 0.606930437, 53, 8, 2.898550725, 6, 3, 0.105072464, 2.307692308, 2.891696751, 0.456, 5],
        ['HK', 0.735632184, 0.607909605, 0.738298423, 1645, 84, 2.815348837, 6, 3, 0.012093023, 3.542857143, 2.813875312, 0.476, 11],
        ['HN', 0.402298851, 0.537853107, 0.589475045, 3, 4, 3.177011494, 6, 3, 0.07816092, 2.266666667, 3.177011494, 0.512, 3],
        ['HR', 0.655172414, 0.661016949, 0.759503491, 51, 6, 3.187946885, 7, 4, 0.030898876, 2.64516129, 3.186830015, 0.509, 8],
        ['HT', 0.540229885, 0.30960452, 0.772950608, 1, 1, 1.8, 3, 2, 0.4, 1.6, 1.8, 0.219, 2],
        ['HU', 0.701149425, 0.657627119, 0.742435997, 136, 14, 3.210277492, 6, 3, 0.017060637, 2.175675676, 3.853757907, 0.697, 11],
        ['ID', 0.551724138, 0.663276836, 0.570338764, 123, 53, 3.426877705, 9, 5, 0.006878711, 3.735338346, 3.630971155, 0.598, 14],
        ['IE', 0.931034483, 0.863276836, 0.952417895, 311, 29, 4.020050125, 8, 4, 0.040100251, 1.974358974, 4.001196172, 0.703, 14],
        ['IL', 0.770114943, 0.740112994, 0.68231187, 185, 14, 2.64516129, 6, 3, 0.017088056, 3.14893617, 2.655762885, 0.399, 9],
        ['IN', 0.689655172, 0.772881356, 0.573700543, 259, 24, 2.663390723, 6, 3, 0.004868247, 3.899014778, 2.705581506, 0.433, 13],
        ['IQ', 0.32183908, 0.355932203, 0.479700026, 9, 4, 2.809411765, 6, 3, 0.054901961, 2.745098039, 2.809411765, 0.47, 6],
        ['IR', 0.057471264, 0.101694915, 0.162141195, 8, 10, 3.037163761, 6, 3, 0.010847013, 3.144578313, 3.247988935, 0.555, 12],
        ['IS', 0.954022989, 0.960451977, 0.917895009, 70, 9, 2.753535354, 5, 3, 0.074747475, 2.622222222, 3.013274336, 0.488, 6],
        ['IT', 0.735632184, 0.764971751, 0.735971037, 1390, 109, 2.853935175, 6, 4, 0.009845909, 5.843505477, 2.940350567, 0.416, 11],
        ['JM', 0.908045977, 0.71299435, 0.952676493, 9, 3, 2.095238095, 4, 2, 0.285714286, 1.714285714, 2.095238095, 0.292, 3],
        ['JO', 0.390804598, 0.302824859, 0.55327127, 3, 1, 2.92, 6, 3, 0.1, 2.4, 2.92, 0.445, 3],
        ['JP', 0.862068966, 0.790960452, 0.748771658, 431, 84, 2.880283782, 6, 3, 0.007965682, 4.148820327, 2.915195512, 0.455, 12],
        ['KE', 0.517241379, 0.457627119, 0.682570468, 40, 13, 2.772108844, 6, 3, 0.067176871, 3.019607843, 2.671799808, 0.455, 7],
        ['KG', 0.32183908, 0.470056497, 0.700413757, 5, 3, 3, 6, 3, 0.132352941, 1.833333333, 2.936170213, 0.584, 7],
        ['KH', 0.390804598, 0.418079096, 0.567235583, 101, 7, 2.984901278, 6, 3, 0.076655052, 3.142857143, 2.984901278, 0.431, 5],
        ['KR', 0.747126437, 0.788700565, 0.753943626, 165, 17, 2.548162476, 6, 3, 0.005230496, 3.679432624, 2.550955029, 0.397, 13],
        ['KW', 0.459770115, 0.305084746, 0.698474269, 50, 8, 3.028019324, 7, 4, 0.060869565, 2.739130435, 3.028019324, 0.448, 5],
        ['KZ', 0.183908046, 0.236158192, 0.405999483, 55, 9, 2.869286287, 6, 3, 0.036086608, 2.76744186, 3.032010944, 0.508, 7],
        ['LA', 0.149425287, 0.127683616, 0.175976209, 1, 1, 1.866666667, 3, 2, 0.333333333, 1.666666667, 1.866666667, 0.22, 2],
        ['LB', 0.528735632, 0.456497175, 0.685932247, 4, 3, 2.390966309, 4, 2, 0.034061459, 2.351351351, 2.422436135, 0.456, 4],
        ['LK', 0.287356322, 0.520903955, 0.31781743, 58, 3, 1.942857143, 3, 2, 0.219047619, 2.4, 2.228571429, 0.31, 4],
        ['LT', 0.850574713, 0.729943503, 0.854150504, 67, 10, 3.033176594, 7, 4, 0.032915361, 2.782608696, 3.032114883, 0.55, 8],
        ['LU', 0.977011494, 0.881355932, 0.921256788, 122, 22, 2.894736842, 6, 3, 0.058321479, 2.1, 2.892045455, 0.507, 7],
        ['LV', 0.804597701, 0.723163842, 0.86294285, 89, 8, 3.262270942, 6, 4, 0.015161431, 2.895833333, 3.262270942, 0.524, 8],
        ['MA', 0.333333333, 0.329943503, 0.590509439, 3, 1, 1.8, 3, 2, 0.4, 1.6, 1.8, 0.219, 2],
        ['ME', 0.712643678, 0.549152542, 0.649469873, 4, 4, 3.384615385, 8, 4, 0.166666667, 2, 3.384615385, 0.429, 4],
        ['MG', 0.390804598, 0.37740113, 0.742565296, 12, 1, 1, 1, 1, 1, 1, 1, 0, 1],
        ['MM', 0.137931034, 0.22259887, 0.553141971, 2, 2, 2.19047619, 4, 2, 0.285714286, 1.555555556, 2.136363636, 0.459, 3],
        ['MN', 0.689655172, 0.625988701, 0.770752521, 8, 2, 2.514935989, 5, 3, 0.056899004, 2.105263158, 2.514935989, 0.373, 7],
        ['MR', 0.517241379, 0.349152542, 0.770493923, 2, 1, 1, 1, 1, 1, 1, 1, 0, 1],
        ['MT', 0.862068966, 0.825988701, 0.784846134, 9, 5, 2.58008658, 5, 3, 0.116883117, 2.454545455, 2.58008658, 0.445, 4],
        ['MW', 0.425287356, 0.517514124, 0.755753814, 3, 2, 1.666666667, 3, 2, 0.5, 1, 1, 0, 1],
        ['MX', 0.402298851, 0.632768362, 0.5323248, 44, 18, 3.232955536, 8, 4, 0.017494914, 3.212765957, 3.232825758, 0.515, 10],
        ['MY', 0.390804598, 0.611299435, 0.537496768, 195, 16, 3.388370188, 7, 4, 0.025061425, 2.580645161, 3.385408147, 0.599, 12],
        ['MZ', 0.620689655, 0.404519774, 0.709594001, 3, 2, 3, 6, 3, 0.222222222, 1.777777778, 3, 0.398, 3],
        ['MU', 0.781609195, 0.801129944, 0.739203517, 530, 6, 2.581818182, 4, 2, 0.181818182, 1.714285714, 2.517241379, 0.531, 4],
        ['NA', 0.747126437, 0.583050847, 0.935608999, 51, 3, 1.6, 2, 1, 0.4, 1.5, 1.538461538, 0.444, 2],
        ['NG', 0.540229885, 0.302824859, 0.65645203, 43, 5, 3.268514851, 7, 4, 0.027128713, 2.712871287, 3.268514851, 0.535, 7],
        ['NL', 0.977011494, 0.885875706, 0.978019136, 1957, 223, 2.91980781, 8, 1, 0.016605094, 9.215827338, 2.91980781, 0.242, 12],
        ['NO', 1, 1, 0.997026118, 558, 31, 3.465031689, 8, 5, 0.015210802, 2.870466321, 3.464895845, 0.579, 11],
        ['NP', 0.482758621, 0.416949153, 0.674295319, 3, 3, 3.748663102, 9, 5, 0.07486631, 2.470588235, 3.748663102, 0.545, 6],
        ['NZ', 0.91954023, 0.924293785, 0.967158004, 63, 29, 3.984911342, 8, 5, 0.010270994, 2.491935484, 3.984645235, 0.684, 13],
        ['OM', 0.298850575, 0.233898305, 0.59516421, 59, 3, 1.6, 3, 2, 0.466666667, 2.333333333, 1.6, 0.071, 2],
        ['PA', 0.586206897, 0.677966102, 0.72252392, 18, 6, 2.86440678, 7, 4, 0.044632768, 2.580645161, 2.863354037, 0.454, 8],
        ['PE', 0.609195402, 0.616949153, 0.693690199, 16, 6, 2.363636364, 5, 3, 0.181818182, 1.7, 2.376623377, 0.602, 6],
        ['PG', 0.804597701, 0.559322034, 0.762735971, 3, 1, 1.785714286, 3, 2, 0.321428571, 2.25, 1.785714286, 0.179, 3],
        ['PH', 0.632183908, 0.642937853, 0.564649599, 104, 18, 2.864605959, 7, 4, 0.019214703, 3.2, 3.100696185, 0.514, 6],
        ['PK', 0.390804598, 0.402259887, 0.444789242, 49, 4, 2.71963964, 6, 3, 0.042162162, 3.066666667, 2.776216216, 0.425, 6],
        ['PL', 0.827586207, 0.722033898, 0.932893716, 121, 49, 3.783136735, 10, 6, 0.00194753, 3.292941176, 3.783129677, 0.624, 22],
        ['PT', 0.91954023, 0.75819209, 0.876002069, 330, 12, 3.663740123, 7, 4, 0.035996488, 2.411764706, 3.663740123, 0.595, 7],
        ['PY', 0.425287356, 0.585310734, 0.660977502, 1, 1, 2.391812866, 4, 2, 0.128654971, 2.181818182, 2.373563218, 0.487, 4],
        ['QA', 0.344827586, 0.237288136, 0.640160331, 85, 1, 2.277777778, 5, 3, 0.277777778, 2.222222222, 2.277777778, 0.245, 4],
        ['RO', 0.643678161, 0.632768362, 0.775277993, 262, 29, 3.999791375, 8, 5, 0.002728179, 2.692836114, 3.999745753, 0.665, 28],
        ['RS', 0.712643678, 0.636158192, 0.739591415, 90, 18, 2.843628876, 5, 3, 0.025314922, 3.203007519, 2.84828558, 0.454, 10],
        ['RU', 0.195402299, 0.261016949, 0.515774502, 2137, 252, 3.418580926, 8, 4, 0.001104512, 4.89740699, 3.418580926, 0.506, 20],
        ['RW', 0.172413793, 0.24519774, 0.365787432, 9, 5, 1.777777778, 3, 2, 0.333333333, 2.6, 1.911111111, 0.189, 2],
        ['SA', 0.149425287, 0.083615819, 0.32906646, 31, 9, 2.862970297, 5, 3, 0.031683168, 3.168316832, 2.862970297, 0.448, 7],
        ['SD', 0.218390805, 0.164971751, 0.161882596, 4, 2, 1.466666667, 2, 1, 0.533333333, 2.666666667, 1.466666667, 0, 1],
        ['SE', 1, 0.97740113, 0.974786656, 1511, 50, 3.405095627, 8, 5, 0.006789688, 2.856470588, 3.40506868, 0.607, 14],
        ['SG', 0.344827586, 0.559322034, 0.504137574, 477, 32, 2.867982194, 6, 3, 0.018404093, 3.120879121, 2.862478666, 0.516, 11],
        ['SI', 0.827586207, 0.733333333, 0.831523145, 73, 9, 3.130183916, 7, 4, 0.013667508, 3.225, 3.127336123, 0.473, 9],
        ['SK', 0.873563218, 0.708474576, 0.946470132, 438, 10, 3.372727273, 7, 4, 0.028484848, 2.75, 3.371768982, 0.578, 9],
        ['SN', 0.482758621, 0.572881356, 0.738169123, 4, 1, 1, 1, 1, 1, 1, 1, 0, 1],
        ['SZ', 0.24137931, 0.227118644, 0.485906387, 1, 1, 1.333333333, 2, 1, 0.666666667, 1.333333333, 1.333333333, 0, 1],
        ['TH', 0.425287356, 0.48700565, 0.579131109, 114, 23, 3.228462649, 8, 4, 0.012168417, 3.375438596, 3.361768244, 0.558, 10],
        ['TJ', 0.206896552, 0.145762712, 0.629299198, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
        ['TN', 0.528735632, 0.590960452, 0.597103698, 1, 1, 1.928571429, 3, 2, 0.25, 1.75, 1.928571429, 0.194, 2],
        ['TR', 0.482758621, 0.456497175, 0.526247737, 42, 14, 2.677732767, 5, 3, 0.00795376, 2.693409742, 2.727629022, 0.514, 14],
        ['TT', 0.827586207, 0.66779661, 0.807732092, 5, 2, 2.055555556, 5, 3, 0.305555556, 2.444444444, 2.055555556, 0.145, 2],
        ['TW', 0.827586207, 0.742372881, 0.776183088, 133, 20, 2.982196268, 6, 3, 0.029767839, 3.512605042, 2.982196268, 0.479, 7],
        ['TZ', 0.551724138, 0.529943503, 0.734031549, 21, 8, 3.508536585, 8, 4, 0.053658537, 2.042553191, 3.492140266, 0.623, 8],
        ['UA', 0.436781609, 0.49039548, 0.591673132, 1777, 123, 3.855507497, 10, 5, 0.002043496, 3.112125163, 3.856174746, 0.645, 24],
        ['UG', 0.459770115, 0.46779661, 0.688001034, 22, 9, 3.116959064, 7, 4, 0.128654971, 2.210526316, 2.861313869, 0.493, 4],
        ['US', 0.908045977, 0.794350282, 0.781613654, 6830, 576, 3.338579299, 10, 1, 2.92E-04, 4.529684482, 3.338579299, 0.538, 34],
        ['UY', 0.816091954, 0.801129944, 0.891130075, 39, 4, 2.274725275, 5, 3, 0.21978022, 2.857142857, 2.274725275, 0.249, 4],
        ['UZ', 0.022988506, 0.15480226, 0.306697698, 10, 6, 2.806324111, 6, 3, 0.090909091, 1.928571429, 2.760456274, 0.538, 4],
        ['VE', 0.24137931, 0.450847458, 0.572148953, 49, 8, 2.681681682, 5, 3, 0.078078078, 2.65, 2.759342302, 0.513, 5],
        ['VN', 0.149425287, 0.263276836, 0.15813292, 33, 7, 2.888200894, 6, 3, 0.021121431, 3.590643275, 2.888200894, 0.441, 9],
        ['ZA', 0.724137931, 0.761581921, 0.811998966, 585, 35, 2.630511717, 5, 3, 0.020468675, 4.165048544, 2.637035283, 0.407, 6],
        ['ZM', 0.425287356, 0.6, 0.653090251, 1, 1, 1.6, 2, 1, 0.4, 1.6, 1.6, 0, 1],
        ['ZW', 0.195402299, 0.192090395, 0.590509439, 4, 4, 2.272727273, 5, 3, 0.218181818, 1.636363636, 1.918918919, 0.327, 3]
    ]

class Cluster:
    def __init__(self):
        self.INDEXES = []
        self.METRICS = []

    # Plot scatter and CDF using metrics and indexes!
    def plot_metric_indexes(self):
        def normalize(M):
            metrics = filter(lambda x: x >= 0, M)
            assert len(metrics) == len(M), "Negative value found in the given metric!"
            max_metric, min_metric = max(metrics), min(metrics)
            for i in range(len(M)):
                metrics[i] = (metrics[i] - min_metric) / float(max_metric - min_metric)
            return metrics

        def popup_plot(target, colors):
            plot_num = 1
            plt.figure(figsize=(8 * 2 + 5, 12))
            plt.subplots_adjust(left=.02, right=.98, bottom=.02, top=.96, wspace=.3, hspace=.15)
            plt.grid(True)
            plt.xticks(())
            plt.yticks(())

            for i, X in enumerate(self.INDEXES):
                for j, Y in enumerate(self.METRICS):
                    axes = plt.gca()
                    axes.set_xlim([0, 1])
                    axes.set_ylim([0, 1])
                    plt.subplot(3, 10, plot_num)
                    plt.title(data_labels[i+1] + ' - ' + data_labels[j+4], size=11)

                    if target == 'scatter':
                        index_metric = [(x, y) for x, y in zip(X, Y) if x >= 0 and y >= 0]
                        plt.scatter(np.array([x for x, y in index_metric]), np.array([y for x, y in index_metric]),
                                    color=colors[data_labels[i+1]])
                        #plt.text(.01, .95, ('CorrCoef: %.4f' % np.corrcoef(X, Y, bias=0)[1, 0]),
                        #         transform=plt.gca().transAxes, size=12, horizontalalignment='left')

                    elif target == 'cdf':
                        #plt.legend(loc='lower right')
                        for d, label, color in zip([X, Y], sorted(colors.keys()), [colors[x] for x in sorted(colors.keys())]):
                            sorted_data = np.sort(d)
                            y = np.arange(len(sorted_data)) / float(len(sorted_data))
                            plt.plot(sorted_data, y, c=color, label=label)

                    plot_num += 1

            plt.show()
            plt.close()

        data_labels = ['CC', 'FHI', 'DI', 'RWBI', 'foreign asns', 'asns_out_conn',
                       'shortest_path', 'diameter', 'radius', 'density', 'degree',
                       'average path', 'modularity', 'community number']

        metrics_per_country = {}
        for d in dataset:
            metrics_per_country[d[0]] = d[1:]

        # Normalize all metrics!
        # (i+3)th metric matches the jth normalized value in a country 'cc'
        all_metrics = zip(*dataset)[4:]
        for i, metric in zip(range(len(all_metrics)), all_metrics):
            norm_values = normalize(list(metric))
            for j, cc in zip(range(len(norm_values)), sorted(metrics_per_country.keys())):
                metrics_per_country[cc][i+3] = norm_values[j]

        self.INDEXES = [list(index) for index in zip(*dataset)[1:4]]                             # FHI, DI, RWBI
        self.METRICS = [list(metric) for metric in zip(*metrics_per_country.values())[3:]]       # M1 ~ M10
        #print 'CorrCoef(%s, %s) = %.4f' % (index_label, metric_label, np.corrcoef(X, Y, bias=0)[1, 0])

        # A. CDF of each index (FHI, DI, RWBI)
        util.cdf_plot(list(zip(*metrics_per_country.values()))[0:3], {'1. FHI': 'green', '2. DI': 'red', '3. RWBI': 'blue'})

        # B. Scatter plot between indexes and metrics
        popup_plot('scatter', {'FHI': 'blue', 'DI': 'green', 'RWBI': 'red'})

        # C. CDF plot between indexes and metrics
        popup_plot('cdf', {'METRIC': 'red', 'INDEX': 'green'})


    def cluster_comparison(self, n_clusters):
        # Attempt 8 different clustering algorithms with n clusters
        def cluster_plot(datasets, n_clusters, ds):
            colors = np.array([x for x in 'bgrcmykbgrcmykbgrcmykbgrcmyk'])
            #colors = np.hstack([colors] * 20)

            clustering_names = ['MiniBatchKMeans', 'AffinityPropagation', 'MeanShift',
                                'SpectralClustering', 'Ward', 'AgglomerativeClustering', 'DBSCAN', 'Birch']

            plt.figure(figsize=(len(clustering_names) * 2 + 3, 9.5))
            plt.subplots_adjust(left=.02, right=.98, bottom=.001, top=.96, wspace=.05, hspace=.01)

            data_labels = ['CC', 'FHI', 'DI', 'RWBI', 'foreign asns', 'asns_out_conn',
                                   'shortest_path', 'diameter', 'radius', 'density', 'degree',
                                   'average path', 'modularity', 'community number']

            # Per each 4 dataset, this part generates 8 x 4 different subplots for clustering!!
            plot_num = 1
            for i_dataset, dataset in enumerate(datasets):
                # normalize dataset for easier parameter selection
                X = StandardScaler().fit_transform(dataset)
                # estimate bandwidth for mean shift
                bandwidth = cluster.estimate_bandwidth(X, quantile=0.3)
                # connectivity matrix for structured Ward and connectivity symmetric
                connectivity = kneighbors_graph(X, n_neighbors=10, include_self=False)
                connectivity = 0.5 * (connectivity + connectivity.T)

                # create clustering estimators
                two_means = cluster.MiniBatchKMeans(n_clusters=n_clusters)
                affinity_propagation = cluster.AffinityPropagation(damping=.9, preference=-200)
                ms = cluster.MeanShift(bandwidth=bandwidth, bin_seeding=True)
                spectral = cluster.SpectralClustering(n_clusters=n_clusters, eigen_solver='arpack', affinity="nearest_neighbors")
                ward = cluster.AgglomerativeClustering(n_clusters=n_clusters, linkage='ward', connectivity=connectivity)
                average_linkage = cluster.AgglomerativeClustering(linkage="average", affinity="cityblock",
                                                                  n_clusters=n_clusters, connectivity=connectivity)
                dbscan = cluster.DBSCAN(eps=.2)
                birch = cluster.Birch(n_clusters=n_clusters)

                clustering_algorithms = [two_means, affinity_propagation, ms, spectral, ward, average_linkage, dbscan, birch]

                for name, algorithm in zip(clustering_names, clustering_algorithms):
                    # predict cluster memberships
                    algorithm.fit(X)
                    if hasattr(algorithm, 'labels_'):
                        y_pred = algorithm.labels_.astype(np.int)
                    else:
                        y_pred = algorithm.predict(X)

                    # Draw subplot
                    plt.subplot(4, len(clustering_algorithms), plot_num)
                    if i_dataset == 0:
                        plt.title(name, size=13)
                    plt.scatter(X[:, 0], X[:, 1], color=colors[y_pred].tolist(), s=10)

                    if hasattr(algorithm, 'cluster_centers_'):
                        centers = algorithm.cluster_centers_
                        center_colors = colors[:len(centers)]
                        plt.scatter(centers[:, 0], centers[:, 1], s=100, c=center_colors)

                    plt.xlim(-2, 2)
                    plt.ylim(-2, 2)
                    plt.xticks(())
                    plt.yticks(())
                    plot_num += 1
                    if name in ['MiniBatchKMeans', 'SpectralClustering', 'Ward', 'AgglomerativeClustering', 'Birch']:
                        plt.text(.99, .01, ('cluster=%d, %s' % (n_clusters, data_labels[i_dataset + ds + 4])),
                                 transform=plt.gca().transAxes, size=12, horizontalalignment='right')
                    else:
                        plt.text(.99, .01, ('%s' % (data_labels[i_dataset + ds + 4])),
                                 transform=plt.gca().transAxes, size=12, horizontalalignment='right')
            plt.show()

        datasets_all = []
        for i in range(4, 14):
            datasets_all.append(np.array([[d[1], d[i]] for d in dataset]))

        for ds in range(0, 12, 4):
            cluster_plot(datasets_all[ds:ds + 4], n_clusters, ds)

    '''
    Algorithms for Graph Similarity and Subgraph Matching
    https://www.cs.cmu.edu/~jingx/docs/DBreport.pdf
    Metric for affinix matrix: simlarity
    '''
    def select_k(self, spectrum, minimum_energy = 0.9):
        running_total = 0.0
        total = sum(spectrum)
        if total == 0.0:
            return len(spectrum)
        for i in range(len(spectrum)):
            running_total += spectrum[i]
            if running_total / total >= minimum_energy:
                return i + 1
        return len(spectrum)

    def calc_similarity(self, G1, G2):
        # Get laplacian
        L1 = nx.spectrum.laplacian_spectrum(G1) 
        L2 = nx.spectrum.laplacian_spectrum(G2)

        k1 = self.select_k(L1)
        k2 = self.select_k(L2)
        k = min(k1, k2)

        similarity = sum((L1[:k] - L2[:k])**2)
        r = 999999999 if similarity == 0 else round(1/similarity, 8)
        return r
        #return similarity
        
    def spec_cluster(self, aff_matrix):
        labels = spectral_clustering(aff_matrix, n_clusters=15, eigen_solver='arpack')
        plt.scatter(aff_matrix[:,:], aff_matrix[:,:], alpha=0.5)
        plt.show()
        return labels

# This part requires thorough testing.. (Not used for now)
def graph_smiliraty_test():
    C = Cluster()
    G = draw_graph.Graph()
    G.get_vertex_edge_per_country()
    G.create_all_graphs()

    all_countries = sorted(G.get_all_countries())
    similarity_comb = [x for x in sorted(itertools.combinations(all_countries, 2))]
    m_size = len(all_countries)

    index_matrix = dict()
    for i, cc in enumerate(all_countries):
        index_matrix[cc] = i

    affinity = np.zeros(shape=(m_size, m_size))

    '''
        a,    b,    c,    d,    e
    a (0,0) (0,1) (0,2) (0,3) (0,4)
    b (1,0) (1,1) (1,2) (1,3) (1,4)
    c (2,0) (2,1) (2,2) (2,3) (2,4)
    d (3,0) (3,1) (3,2) (3,3) (3,4)
    e (4,0) (4,1) (4,2) (4,3) (4,4)
    '''
    print "Size of affinity matrix: %dx%d" % (m_size, m_size)
    for c1, c2 in similarity_comb:
        s = C.calc_similarity(G.get_graph_per_country(c1), G.get_graph_per_country(c2))
        affinity[index_matrix[c1], index_matrix[c2]] = s
        affinity[index_matrix[c2], index_matrix[c1]] = s

    result = C.spec_cluster(affinity).tolist()
    for k, v in sorted(zip(index_matrix.keys(), index_matrix.values())):
        print '%s: Class [%d]' % (k, result[v])

    #print g1.create_graph('AF').nodes(), g1.create_graph('AF').edges()
    #print g2.create_graph('QA').nodes(), g2.create_graph('QA').edges()
    #print c.calc_similarity(g.create_graph('AF'), g.create_graph('QA'))

def metric_index_test():
    C = Cluster()
    C.plot_metric_indexes()

def cluster_test(n_clusters):
    C = Cluster()
    C.cluster_comparison(n_clusters)

if __name__ == '__main__':
    #metric_index_test()
    #cluster_test(5)
    pass