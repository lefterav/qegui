'''
@author: lefterav
'''
import math

from django.utils.translation import ugettext as _
from jchart import Chart
from jchart.config import DataSet, Axes, ScaleLabel, Tick

from qe.models import MachineTranslationEvaluation


class AverageScoreChart(Chart):
    chart_type = 'doughnut'
    options = {
        'rotation': math.pi,
        'circumference': math.pi,
    }
    legend = False
    
    def get_labels(self, *args, **kwargs):
        return ["Average quality score", ""]
    
    def get_datasets(self, average_score, max_score=1.0):
        
        if average_score <= 0.25*max_score:
            color = "DC143C" #red
        elif average_score < 0.5*max_score:
            color = "#FFA07A" #light salmon/orange
        elif average_score < 0.75*max_score:
            color = "#FFD700" #gold
        elif average_score < 0.9*max_score: 
            color = "#98FB98" #palegreen
        else:
            color = "#228B22" #forestgreen
 
        colors = [
            color,
            "#eeeeee"
        ]
        
        leftover = max_score - average_score
        
        return [DataSet(data=[average_score, leftover],
                        label="Average sentence quality score",
                        backgroundColor=colors,
                        hoverBackgroundColor=colors,
                        )]

class ScoreMassChart(Chart):
    chart_type = 'line'
    scales = {
        'xAxes': [Axes(type='linear', 
                       position='bottom',
                       scaleLabel=ScaleLabel(display=True, 
                                             labelString='quality score')
                       )
                  ],
        'yAxes': [Axes(type='linear', 
                       scaleLabel=ScaleLabel(display=True, 
                                             labelString='number of sentences',
                                             ),
                       #ticks={'stepSize': 1},
                       )
                  ],
    }

    def get_datasets(self, document_id):
        
        translation_evaluations = \
            MachineTranslationEvaluation.objects. \
            filter(translation__source__document_id=document_id)
        scores = sorted([round(t.score, 1) for t in translation_evaluations])
        
        q1=0
        q2=0
        q3=0
        q4=0
        
        total = len(scores)
        
        dotsdata = []
        linedata = []
        for score in sorted(list(set(scores))):
            evaluations_per_score = \
                MachineTranslationEvaluation.objects. \
                filter(translation__source__document_id=document_id,
                       score=score).count()
                   
            dotsdata.append({'x': score, 'y': 100.0*evaluations_per_score/total})
            
            # split in quartiles:

            
        #for score in scores:
        #    if score < 0.25:
        #        q1+=1
        #    elif score < 0.5:
        #        q2+=1
        #    elif score < 0.75:
        #        q3+=1
        #    else:
        #        q4+=1
        
        #total = total*25
        
        #linedata.append({'x': 0, 'y': q1*100.0/total})
        #linedata.append({'x': 0.5, 'y': q2*100.0/total})
        #linedata.append({'x': 0.75, 'y': q3*100.0/total})
        #linedata.append({'x': 1.00, 'y': q4*100.0/total})
        #linedata.append({'x': 1.0, 'y': q4*100.0/total})

            
        return [
                #DataSet(type='line',
                #        data=linedata, 
                #        label="quartile tension line",
                #        pointRadius=1,
                #        fill=False,
                #        ),
                DataSet(type='line',
                        data=dotsdata, 
                        label="mass per decimile",
                        pointRadius=1,
                        ),
                ]
        