from unittest import TestCase

import numpy as np
from numpy import ma

from pose_format.pose import Pose
from pose_format.pose_header import PoseNormalizationInfo
from pose_format.utils.normalization_3d import PoseNormalizer


class Test3DNormalization(TestCase):
    """
    Test cases for 3D Normalization of pose data.
    """

    def test_normal(self):
        """
        Test the calculation of the normal vector for given 3 points on a plane.

        Note
        ----

        See the description and calculations on `link`_.

        Example (Plane Equation Example revisited) Given,
        P = (1, 1, 1), Q = (1, 2, 0), R = (-1, 2, 1).
        The normal vector A is the cross product (Q - P) x (R - P) = (1, 2, 2)

        .. _link: https://sites.math.washington.edu/~king/coursedir/m445w04/notes/vector/normals-planes.html#:~:text=Thus%20for%20a%20plane%20(or,4%2B4)%20%3D%203.
        """
        p1 = (1, 1, 1)
        p2 = (1, 2, 0)
        p3 = (-1, 2, 1)

        gold_normal = (1, 2, 2)

        plane = PoseNormalizationInfo(p1=0, p2=1, p3=2)
        normalizer = PoseNormalizer(plane=plane, line=None)
        tensor = ma.array([[p1, p2, p3]], dtype=np.float32)
        normal, _ = normalizer.get_normal(tensor)

        gold_vec = ma.array(gold_normal) / np.linalg.norm(gold_normal)
        self.assertEqual(ma.allclose(normal, gold_vec), True)

    def test_rotate_vector_by_90_degrees(self):
        """
        Test the rotation of a vector by 90 degrees.
        """
        plane = PoseNormalizationInfo(p1=0, p2=1, p3=2)
        line = PoseNormalizationInfo(p1=0, p2=1)
        normalizer = PoseNormalizer(plane, line)

        vector = ma.array([[[1, 0, 0]], [[0, 1, 0]]], dtype=float)  # Shape (1, 1, 3)

        rotated_vector = normalizer.rotate(vector, np.array(90))

        expected_rotated_vector = np.array([[[0, -1, 0]], [[1, 0, 0]]], dtype=float)

        print("rotated_vector", rotated_vector.shape)
        print("expected_rotated_vector", expected_rotated_vector.shape)

        assert np.allclose(rotated_vector, expected_rotated_vector, atol=1e-5)

    def test_hand_normalization(self):
        """
        Test the normalization of hand pose data using the PoseNormalizer.
        """
        with open('tests/data/mediapipe.pose', 'rb') as f:
            pose = Pose.read(f.read())
            pose = pose.get_components(["RIGHT_HAND_LANDMARKS"])

        plane = pose.header.normalization_info(p1=("RIGHT_HAND_LANDMARKS", "WRIST"),
                                               p2=("RIGHT_HAND_LANDMARKS", "PINKY_MCP"),
                                               p3=("RIGHT_HAND_LANDMARKS", "INDEX_FINGER_MCP"))
        line = pose.header.normalization_info(p1=("RIGHT_HAND_LANDMARKS", "WRIST"),
                                              p2=("RIGHT_HAND_LANDMARKS", "MIDDLE_FINGER_MCP"))
        normalizer = PoseNormalizer(plane=plane, line=line, size=100)
        tensor = normalizer(pose.body.data)

        pose.body.data = tensor
        pose.focus()

        with open('tests/data/mediapipe_hand_normalized.pose', 'rb') as f:
            pose_gold = Pose.read(f.read())

        self.assertTrue(ma.allclose(pose.body.data, pose_gold.body.data))

    def test_hand_normalization_results(self):
        """
        Test the normalization results of hand data taken from sign translate.
        """
        # Normalization results taken from sign translate
        NORMALIZATIONS = [[
            [
                [248.66639614105225, 297.9550790786743, -0.08617399376817048],
                [313.59346628189087, 319.78081941604614, 62.890407741069794],
                [349.8637819290161, 310.3189992904663, 104.9409145116806],
                [356.05104207992554, 306.42510890960693, 139.85478281974792],
                [354.0298342704773, 308.7967085838318, 171.05390071868896],
                [368.4513807296753, 211.83621287345886, 118.45286011695862],
                [391.60820722579956, 184.4913125038147, 179.64956641197205],
                [408.85960578918457, 166.19417786598206, 214.12095069885254],
                [418.72357845306396, 153.56018781661987, 241.38201117515564],
                [326.7276906967163, 189.34702157974243, 121.67787551879883],
                [334.95264768600464, 154.9160075187683, 211.92330718040466],
                [338.9851450920105, 145.05938053131104, 276.44052267074585],
                [340.1783061027527, 143.3175253868103, 319.86109495162964],
                [281.5382671356201, 184.43811058998108, 123.64041864871979],
                [288.3403015136719, 189.4317603111267, 214.801185131073],
                [288.1521964073181, 213.1494927406311, 234.93002772331238],
                [285.52247524261475, 227.414470911026, 237.48689651489258],
                [242.2289800643921, 187.8385078907013, 128.50980401039124],
                [246.59330368041992, 202.5400733947754, 196.4439833164215],
                [247.15078473091125, 223.4764289855957, 208.9101231098175],
                [244.32156801223755, 234.57125186920166, 211.09885573387146],
            ],
            [
                [0.0, 0.0, 0.0],
                [-53.87460867272204, -66.96863447520207, 56.796408965708935],
                [-73.72715283958682, -123.0910500437069, 75.20279417200432],
                [-67.90506838734477, -155.96881391642683, 96.28995223458003],
                [-57.40134100627323, -178.19614573765904, 120.84104646210801],
                [-50.965779993758964, -202.95828207912479, -1.509903313490213e-14],
                [-45.260072782063325, -278.98544696979855, 18.405850951171615],
                [-45.1386394307463, -325.57145063545363, 25.90184983567872],
                [-41.976756680249935, -359.5037258132442, 33.766177611013816],
                [-1.0464064364675199e-13, -199.6193245295997, -12.333907505180624],
                [31.975990322228963, -295.8878599646533, 22.44664078562626],
                [51.10130687673754, -354.78374037306935, 59.9347720675275],
                [63.63850727086251, -390.7021194588825, 89.44223523582745],
                [47.39541430043801, -182.86125824655022, -10.404736003411728],
                [66.17638974840436, -254.99061010637854, 58.3901382417529],
                [63.46550446035822, -256.24342044957825, 92.80607773270395],
                [61.464656345964585, -248.2688837751719, 106.9255087795864],
                [86.67900485407291, -166.0742098923334, -1.3322676295501878e-14],
                [97.22986231282657, -212.75611112692522, 60.58942546045143],
                [92.521597827552, -210.01652471672483, 87.09737972755666],
                [91.80539351622573, -203.60235428380585, 98.30312193502695],
            ],
        ],
                          [
                              [
                                  [266.67819833755493, 322.85115814208984, -0.04363307822495699],
                                  [220.46386861801147, 237.49959421157837, -6.432308048009872],
                                  [212.651225566864, 175.74850010871887, 27.4957894384861],
                                  [253.3728199005127, 150.05188155174255, 57.6715869307518],
                                  [290.9366660118103, 158.14260911941528, 97.49647510051727],
                                  [196.53551816940308, 183.21415996551514, 117.52972221374512],
                                  [180.0925350189209, 143.85282921791077, 150.1890881061554],
                                  [170.33970069885254, 121.17275738716125, 186.817076921463],
                                  [165.10530018806458, 101.94312655925751, 224.22807431221008],
                                  [232.6294367313385, 191.9170138835907, 124.57139778137207],
                                  [241.98445081710815, 147.45505690574646, 172.8555293083191],
                                  [247.0248293876648, 124.05966544151306, 195.77275156974792],
                                  [248.24022006988525, 114.18103969097137, 227.97385263442993],
                                  [267.1261944770813, 208.61302876472473, 117.41860234737396],
                                  [277.41753005981445, 168.1429328918457, 110.84358942508698],
                                  [274.5585584640503, 183.77042746543884, 73.29665148258209],
                                  [267.15885734558105, 202.62700247764587, 68.34884583950043],
                                  [300.5849003791809, 226.72553181648254, 112.3670688867569],
                                  [307.9186568260193, 195.0516927242279, 104.11798548698425],
                                  [297.57420539855957, 204.44280195236206, 80.27082800865173],
                                  [286.06309032440186, 217.2321858406067, 73.97288680076599],
                              ],
                              [
                                  [0.0, 0.0, 0.0],
                                  [-54.479260198097805, -71.11846055086438, 58.17594848846076],
                                  [-54.39223415540774, -145.6437901306979, 78.54576783252529],
                                  [-3.545339962524018, -179.63888643031996, 87.61257240473797],
                                  [49.14794301931342, -194.95344154721718, 62.06021751253273],
                                  [-40.09854676422485, -208.82027169070966, 5.551115123125783e-16],
                                  [-48.13049962464756, -266.6680014062149, 1.3281840284453539],
                                  [-47.00941869901266, -313.07001717228695, -11.447169097370368],
                                  [-40.773818965790895, -356.4530129101176, -26.203968571403916],
                                  [9.134429734859657e-15, -199.99294837298712, -1.6794645217193471],
                                  [23.603763878904314, -268.1038602115065, -0.7067006484911872],
                                  [35.301688782987696, -302.1004761871728, 1.720669069409734],
                                  [46.93353477547328, -333.09716362043764, -14.541999919797409],
                                  [34.07355106941323, -174.87454913669825, 0.6581788197466907],
                                  [40.2663401403231, -199.59555645909575, 40.242655464274804],
                                  [25.438899509841193, -160.53426324779335, 55.575838830821],
                                  [17.1508731893172, -143.6797255930755, 42.43293329268436],
                                  [67.86518085896179, -150.39315561348292, 9.103828801926284e-15],
                                  [70.91657215646, -167.61675658262482, 33.11742629384811],
                                  [52.6709032860349, -144.92204539941508, 40.80547628453034],
                                  [39.35404239471322, -132.63262286274133, 32.23603583001071],
                              ],
                          ],
                          [
                              [
                                  [2.60705627e2, 3.37643646e2, -9.28593054e-2],
                                  [2.10784332e2, 3.16998627e2, -8.27554855e1],
                                  [1.93835342e2, 2.66705475e2, -1.24799034e2],
                                  [2.35526871e2, 2.17327255e2, -1.48760818e2],
                                  [2.75498596e2, 1.88349747e2, -1.49933273e2],
                                  [1.71491211e2, 1.91392395e2, -5.14710464e1],
                                  [1.61075333e2, 1.05774673e2, -1.07832794e2],
                                  [1.63360901e2, 5.55294151e1, -1.40600769e2],
                                  [1.73754684e2, 1.11177626e1, -1.5721608e2],
                                  [2.14831955e2, 1.99762024e2, -4.1304863e1],
                                  [2.44172714e2, 1.61405777e2, -1.30912308e2],
                                  [2.38794632e2, 2.27534744e2, -1.27142723e2],
                                  [2.19911545e2, 2.51557541e2, -8.53535767e1],
                                  [2.56865509e2, 2.13906311e2, -4.56171799e1],
                                  [2.84798065e2, 1.86186142e2, -1.3756131e2],
                                  [2.6911795e2, 2.45126968e2, -1.312836e2],
                                  [2.4843277e2, 2.59336426e2, -9.2029335e1],
                                  [2.92065948e2, 2.32734634e2, -5.8856884e1],
                                  [3.13212036e2, 2.08028992e2, -1.22773369e2],
                                  [2.95430847e2, 2.51139603e2, -1.24858963e2],
                                  [2.76066742e2, 2.66142792e2, -9.7968811e1],
                              ],
                              [
                                  [0.0, 0.0, 0.0],
                                  [-2.05852102e1, -8.43542239e1, 9.97880671e1],
                                  [-9.5163617, -1.69808429e2, 1.25001397e2],
                                  [6.54616798e1, -2.20523798e2, 1.13256765e2],
                                  [1.23026573e2, -2.37556703e2, 8.68171243e1],
                                  [-4.64094101e1, -2.32186465e2, -1.82238355e-6],
                                  [-1.13881838e1, -3.62578954e2, 1.98150407e1],
                                  [1.93110838e1, -4.35353543e2, 2.87847134e1],
                                  [5.1511044e1, -4.90263213e2, 1.97556152e1],
                                  [2.06700921e-14, -1.9909322e2, -1.90234006e1],
                                  [8.4304534e1, -2.73281319e2, 5.70360486e1],
                                  [5.75141926e1, -1.97081808e2, 9.26397117e1],
                                  [1.01073372e1, -1.57595191e2, 6.21706932e1],
                                  [4.92581982e1, -1.66689775e2, -1.7115462e1],
                                  [1.29823974e2, -2.30243201e2, 6.83153915e1],
                                  [9.14003112e1, -1.65618917e2, 9.95540985e1],
                                  [4.56163097e1, -1.39487004e2, 6.68586078e1],
                                  [9.25816015e1, -1.35992949e2, 2.44384259e-6],
                                  [1.52234167e2, -1.85738665e2, 5.57429433e1],
                                  [1.19207937e2, -1.44327761e2, 8.82483889e1],
                                  [8.00046381e1, -1.22540409e2, 7.03460515e1],
                              ],
                          ]]

        plane = PoseNormalizationInfo(p1=0, p2=17, p3=5)
        line = PoseNormalizationInfo(p1=0, p2=9)
        normalizer = PoseNormalizer(plane=plane, line=line, size=200)
        for hand_input, hand_output in NORMALIZATIONS:
            hand_input_np = ma.array(hand_input).reshape((1, 1, 21, 3))
            hand_output_np = ma.array(hand_output).reshape((1, 1, 21, 3))
            tensor = normalizer(hand_input_np)

            print("tensor", tensor[0, 0, :2])
            print("gold", hand_output_np[0, 0, :2])
            self.assertTrue(ma.allclose(tensor, hand_output_np, atol=1e-4))
