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
        
 
        colors = [
            "#FF6384",
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
                       ticks={'stepSize': 1},
                       )
                  ],
    }

    def get_datasets(self, document_id):
        
        translation_evaluations = \
            MachineTranslationEvaluation.objects. \
            filter(translation__source__document_id=document_id)
        scores = sorted([t.score for t in translation_evaluations])
        
        data = []
        for score in scores:
            evaluations_per_score = \
                MachineTranslationEvaluation.objects. \
                filter(translation__source__document_id=document_id,
                       score=score).count()
                   
            data.append({'x': score, 'y': evaluations_per_score})
        return [DataSet(type='line',
                        data=data, 
                        label="mass per quality score"
                        ),
                ]
        