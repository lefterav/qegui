'''
@author: lefterav
'''
import math

from django.utils.translation import ugettext as _
from jchart import Chart
from jchart.config import DataSet, Axes, ScaleLabel, Tick

from qe.models import MachineTranslationEvaluation
from django.forms.formsets import TOTAL_FORM_COUNT


COLOR_RED = "#DC143C"
COLOR_ORANGE = "#FFA07A" #light salmon/orange
COLOR_YELLOW = "#FFD700" #gold
COLOR_GREEN = "#98FB98" #palegreen
COLOR_DARKGREEN = "#228B22" #forestgreen

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
            color = COLOR_RED #red
        elif average_score < 0.5*max_score:
            color = COLOR_ORANGE
        elif average_score < 0.75*max_score:
            color = COLOR_YELLOW 
        elif average_score < 0.9*max_score: 
            color = COLOR_GREEN
        else:
            color = COLOR_DARKGREEN
 
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
                                             labelString='% of sentences',
                                             ),
                       #ticks={'stepSize': 1},
                       )
                  ],
    }

    def get_datasets(self, document_id):
        
        total = MachineTranslationEvaluation.objects. \
            filter(translation__source__document_id=document_id).count()
    
        count_0 = MachineTranslationEvaluation.objects. \
                filter(translation__source__document_id=document_id,
                       score=0).count()
                       
        count_1 = MachineTranslationEvaluation.objects. \
                filter(translation__source__document_id=document_id,
                       score=1).count()
    
        dotsdata = [{'x': 0, 'y': count_0*100.0/total}]
        #for score in sorted(list(set(scores))):
        step = 0.1
        for min_score in [round(x * step, 4) for x in range(0, 10)]:
            max_score = min_score+step 
            evaluations_per_score = \
                MachineTranslationEvaluation.objects. \
                filter(translation__source__document_id=document_id,
                       score__gte=min_score, 
                       score__lte=max_score).count()
            
            score = (max_score - min_score)*.5 + min_score
            dotsdata.append({'x': score, 'y': 100.0*evaluations_per_score/total})
            
        dotsdata.append({'x': 1, 'y': count_1*100.0/total})
     
            
        return [
                DataSet(type='line',
                        data=dotsdata, 
                        label="mass per decimile",
                        pointRadius=1,
                        ),
                ]

class QuartileChart(Chart):
    chart_type = 'pie'
    
    def get_labels(self, *args, **kwargs):
        return ['1st quartile (0, 0.25)',
                  '2nd quartile (0.25, 0.5)',
                  '3rd quartile (0.5, 0.75)',
                  '4th quartile (0.75, 1.0)',] 
    
    def get_datasets(self, document_id):
        
        q1 = MachineTranslationEvaluation.objects. \
            filter(translation__source__document_id=document_id,
                   score__lte=0.25).count()
        q2 = MachineTranslationEvaluation.objects. \
            filter(translation__source__document_id=document_id,
                   score__gte=0.25,
                   score__lte=0.5).count()
        q3 =  MachineTranslationEvaluation.objects. \
            filter(translation__source__document_id=document_id,
                   score__gte=0.5,
                   score__lte=0.75).count()
        q4 =  MachineTranslationEvaluation.objects. \
            filter(translation__source__document_id=document_id,
                   score__gte=0.75).count()
        total = q1 + q2 + q3 + q4
        q1 = q1 * 100.0 / total
        q2 = q2 * 100.0 / total
        q3 = q3 * 100.0 / total
        q4 = q4 * 100.0 / total
        colors = [COLOR_RED, COLOR_ORANGE, COLOR_YELLOW, COLOR_DARKGREEN]
        
        
        return [DataSet(data=[q1, q2, q3, q4],
                        label="quality quartiles",
                        backgroundColor=colors)
                ]
        
        
