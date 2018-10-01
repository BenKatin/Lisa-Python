# -*- coding: utf-8 -*-
"""
Created on Fri Apr  6 11:25:46 2018

@author: jrubin

This script exists to convert 1_455_Tanh to the more modern self-contained format.  This enables making predictions without TF and self-contained serialized buildFeatureVector.

"""
import tensorflow as tf
import json

config = tf.ConfigProto(log_device_placement=True, allow_soft_placement=False)
config.gpu_options.allow_growth = True # If GPU present, prevents tf from trying to allocate all gpu memory at once and crashing. 

with tf.Session(graph=tf.Graph(), config=config) as session:
    tf.saved_model.loader.load(session, ["tag"], 'models/multi_1_455_Tanh')
    graph = tf.get_default_graph()
    
    modelInfoPath    = 'models\\multi_1_455_Tanh\\info.txt'
    modelInfoPathOut = 'models\\multi_1_455_Tanh\\info.new.txt'

    with open(modelInfoPath) as data_file:    
         modelInfo = json.load(data_file)
        
    buildFeatureVector = '''lambda t, plate, imp, thick : [ 
             1 if plate == 0 else 0,    #  is 384PPG (or PP pre-Lemonade)?
             1 if plate == 1 else 0,    #  is 384PPL?
             1 if plate == 2 else 0,    #  is 384LDV?
             1 if plate == 3 else 0,    #  is 1536LDV?                  
             t['FocalSweepQuadAmpFit']['a'],
             t['FocalSweepQuadAmpFit']['b'],
             t['FocalSweepQuadAmpFit']['c'],
             t['TransducerBandwidthSingleLinearFit']['intercept'],
             t['TransducerBandwidthSingleLinearFit']['slope'],
             t['AmpDetails'][0], # RF Slope1
             t['plateSpecific'][2]['EODetails']['thicknessAtMin'],
             t['plateSpecific'][2]['EODetails']['ejOffAtMin'],
             t['plateSpecific'][2]['EODetails']['ejOffAtMax'],
             t['plateSpecific'][2]['EODetails']['thicknessAtMax'],       
             imp ] # Impedance  '''    
            
    modelInfo['normalization_std']       = list(map(lambda x: x.tolist(), session.run('Const_1:0') + 0.0001)) # Had this extra 0.0001 in the denominator to prevet divide-by-zero in trainier.  Was hard to track down.
    modelInfo['normalization_mean']      = list(map(lambda x: x.tolist(), session.run('Const:0')))
    modelInfo['normalization_targ_std']  = list(map(lambda x: x.tolist(), session.run('Const_3:0')))
    modelInfo['normalization_targ_mean'] = list(map(lambda x: x.tolist(), session.run('Const_2:0')))
    
    modelInfo['layerWeights']            = list(map(lambda x: x.tolist(), session.run(['Hidden_1/Variable:0', 'Hidden_2/Variable:0', 'Logits/Weights:0'])))
    modelInfo['layerBiases']             = list(map(lambda x: x.tolist(), session.run(['Hidden_1/Biases:0',    'Hidden_2/Biases:0',    'Logits/Biases:0' ])))
    
    modelInfo['buildFeatureVector']      = buildFeatureVector
    
    modelInfo['train_dataset'] =    [[-6.052388569485768e-07, 0.020736567299696394, -175.51878651218152, 18.46812501927193, -0.4532733127298886, 54.00671407, 1.5, 133.072, 393.841, 2.65],
                                     [-6.447381244017877e-07, 0.022193654834150704, -188.92250127364406, 17.2608264828932, -0.33882516680945207, 54.00671407, 1.5, 134.187, 400.803, 2.86],
                                     [-6.612937743325578e-07, 0.02309051691454227, -199.48535071252888, 15.754450452354236, -0.21603078337152323, 54.00671407, 1.5, 29.93018, 307.72559, 2.65549],
                                     [-6.060394057327489e-07, 0.021005353465556164, -180.05002618247534, 16.829966773470233, -0.32703059261556233, 54.00671407, 1.5, 102.90677, 358.13135, 3.1],
                                     [-6.172885590252188e-07, 0.01895481862737557, -143.6447452494994, 16.8220448618819, -0.3469033678943591, 53.58584776, 1.5, 49.53719, 327.31122, 2.45], 
                                     [-4.854900625214704e-07, 0.016293987871361777, -134.7729793453471, 17.86512350936983, -0.4322805975119141, 54.00671407, 1.5, 166.571, 473.732, 2.86],
                                     [-7.028209737237162e-07, 0.020791963354820846, -151.36630034463528, 17.804185023680546, -0.3527066012795253, 53.58584776, 1.5, 116.39266, 375.95706, 2.65],
                                     [-7.798388297168433e-07, 0.026953978383159237, -230.4785894381879, 17.716486218736026, -0.33324154377536047, 54.00671407, 1.5, 90.35472, 379.47751, 2.86], 
                                     [-7.527464840374581e-07, 0.025892757349062108, -220.36047845491012, 16.988298863979523, -0.274253688438102, 54.00671407, 1.3, 118.865, 377.859, 2.65],
                                     [-6.768739445198805e-07, 0.020133075418350747, -147.3590702196677, 16.86757723190874, -0.2690807573573543, 53.58584776, 1.5, 80.2288, 375.64148, 2.65],
                                     [-6.026354779870019e-07, 0.018115041495801433, -134.18087001468865, 18.495070454699107, -0.5009959940633238, 53.58584776, 1.65, 69.73221, 328.3121, 2.65], 
                                     [-7.179224680623074e-07, 0.022253590265844968, -170.31017810375235, 17.620130192468444, -0.3606097331699212, 53.58584776, 1.5, 20.4227, 274.77, 2.45], 
                                     [-6.342519314919729e-07, 0.022173396475437958, -191.7442275806552, 18.25780607275947, -0.4226273430183915, 54.00671407, 1.5, 100.567, 342.903, 2.65], 
                                     [-6.458400563039225e-07, 0.01898833784841216, -137.24572398916305, 16.7500343015053, -0.2665079771521513, 53.58584776, 1.5, 124.381, 436.343, 2.86],
                                     [-6.965331076758233e-07, 0.0022070005588672526, 0.2241962166910154, 15.372391699053987, -0.18166273490862062, 54.00671407, 1.5, 23.31067, 286.25717, 2.45],
                                     [-7.428327177817487e-07, 0.025362413412259276, -213.92216867839525, 16.823768421235894, -0.2363928984122192, 54.00671407, 1.3, 139.52892, 411.89908, 2.65]]
    

    with open(modelInfoPathOut,'w+') as f:
         json.dump(modelInfo, f)   