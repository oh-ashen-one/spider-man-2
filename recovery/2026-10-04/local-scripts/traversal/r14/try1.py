run('backDouble r13', -720, [('Tuck',1.0),('Kickout',0.7)], catch=0.2)
I['Kickout']=9.0
run('backDouble A', -720, [('Tuck',1.12,0.9,0.9),('Kickout',0.62)], catch=0.2)
run('backDouble B', -720, [('Tuck',1.15,0.7,0.8),('Kickout',0.62)], catch=0.2)
run('pikeSwan A', 360, [('Pike',0.40,0.6,0.3),('Swan',0.55),('Tuck',0.40,0.6,0.6),('Reach',0.28)])
run('cork A', 360, [('Layout',0.32),('Twist',0.45),('Swan',0.40),('Tuck',0.36,0.6,0.6),('Reach',0.25)])
run('backSingle A', -360, [('Tuck',0.32,0.5,0.3),('Pencil',0.36),('Tuck',0.32,0.3,0.6),('Reach',0.24)])
