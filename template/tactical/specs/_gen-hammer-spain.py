import json, sys
def P(i,t,r,g=None):
    d={"id":i,"team":t,"role":r}
    if g: d["guards"]=g
    return d
def save(spec):
    json.dump(spec, open(f"/home/user/e2a-tiktok-media/template/tactical/specs/{spec['id']}.spec.json","w"), indent=1)

# ---------------- V01 Hammer screen
hp=[P("O1","O","Driver (ball)"),P("O2","O","Shooter, weak-side corner"),P("O3","O","Spacer, ball-side corner"),
    P("O4","O","Hammer screener"),P("O5","O","Trailer, top"),
    P("X1","X","On the ball","O1"),P("X2","X","Low man, weak-side corner","O2"),P("X3","X","Ball-side corner","O3"),
    P("X4","X","On the screener","O4"),P("X5","X","On the trailer","O5")]
hs={"O1":[3.6,7.2],"O2":[-6.6,1.3],"O3":[6.6,1.3],"O4":[-3.6,5.6],"O5":[-1.0,8.6],
    "X1":[3.0,6.6],"X2":[-5.5,2.1],"X3":[5.6,2.1],"X4":[-3.0,4.9],"X5":[-0.8,7.6]}
drive={"at":0.3,"via":[[4.3,4.7]],"to":[2.3,1.9],"speed":6.0}
x1={"at":0.4,"to":[2.2,3.6],"speed":4.0}
common_actions={"X3":[{"type":"stance","from":0,"to":5.5,"face":"O3"}],"X5":[{"type":"stance","from":0,"to":5.5,"face":"O5"}]}
A={"id":"hammer-a-skip","title":"Hammer screen — Case A: the low man helps, skip to the corner","duration":5.5,
 "notes":["O1 drives baseline. X2 (low man) leaves the corner to help at the rim.","O4 sprints down and sets the hammer screen on X2's recovery path (legal: stationary).","O1 skips over the top to O2 in the corner: open three, X2 is pinned inside."],
 "players":hp,"start":hs,
 "legs":{"O1":[drive],"X1":[x1],
   "X2":[{"at":0.7,"to":[-2.2,2.9],"speed":4.6},{"at":2.05,"to":[-3.0,2.7],"speed":2.6},{"at":2.9,"via":[[-3.3,3.7]],"to":[-4.8,3.6],"speed":3.2}],
   "O4":[{"at":0.6,"to":[-4.1,2.5],"speed":4.6}],
   "X4":[{"at":0.8,"to":[-2.2,4.6],"speed":2.0}]},
 "ball":[{"type":"hold","player":"O1","from":0,"to":1.95,"dribble":True},
         {"type":"pass","from":"O1","to":"O2","t0":1.95,"t1":2.75,"style":"overhead"},
         {"type":"hold","player":"O2","from":2.75,"to":3.1},
         {"type":"shot","player":"O2","t0":3.1,"t1":4.2,"make":True}],
 "screens":[],
 "marks":{"start":0,"drive":0.3,"help":0.7,"screen":1.7,"pass":1.95,"catch":2.75,"release":3.1,"make":4.2,"end":5.5},
 "actions":{**common_actions,"O4":[{"type":"screen","from":1.75,"to":3.4,"face":"X2"}],
   "X2":[{"type":"stance","from":0,"to":0.6,"face":"O1"},{"type":"contest","from":3.3,"to":3.9}],
   "X1":[{"type":"stance","from":0,"to":0.4,"face":"O1"}],"X4":[{"type":"stance","from":0,"to":5.5,"face":"O1"}],
   "O2":[{"type":"celebrate","from":4.3,"to":5.3}]},
 "claims":[{"type":"far","a":"X2","b":"O2","at":"pass","min":3.5,"says":"the corner defender leaves his man to stop the drive"},
           {"type":"near","a":"O4","b":"X2","at":"catch","max":1.6,"says":"the hammer screen pins him inside"},
           {"type":"open","player":"O2","at":"release","min":2.0,"says":"open three from the corner"},
           {"type":"behind_arc","player":"O2","at":"catch","says":"open three from the corner"},
           {"type":"order","marks":["drive","help","screen","pass","catch","release","make"],"says":"drive, help, screen, skip, shot"}]}
B={**A,"id":"hammer-b-rim","title":"Hammer screen — Case B: the low man stays home, finish at the rim",
 "notes":["Same spots at 0 s. X2 stays home on O2 (no help).","O4 still sets the hammer screen; with no help, the baseline lane is open.","O1 finishes the layup; the nearest defender (X1) trails."],
 "legs":{"O1":[{"at":0.3,"via":[[4.3,4.7],[3.0,2.6]],"to":[1.0,1.8],"speed":5.5}],"X1":[{"at":0.4,"to":[2.2,3.7],"speed":4.0}],
   "X2":[{"at":0.8,"to":[-5.7,2.3],"speed":1.5}],
   "O4":[{"at":0.6,"to":[-4.1,2.5],"speed":4.6}],
   "X4":[{"at":0.8,"to":[-2.2,4.6],"speed":2.0},{"at":2.0,"to":[-1.2,3.6],"speed":2.5}]},
 "ball":[{"type":"hold","player":"O1","from":0,"to":2.35,"dribble":True},
         {"type":"layup","player":"O1","t0":2.35,"t1":2.75,"make":True}],
 "marks":{"start":0,"drive":0.3,"stay":0.8,"screen":1.7,"release":2.35,"make":2.75,"end":5.5},
 "actions":{**common_actions,"O4":[{"type":"screen","from":1.75,"to":3.4,"face":"X2"}],
   "X2":[{"type":"stance","from":0,"to":5.5,"face":"O2"}],
   "X1":[{"type":"stance","from":0,"to":0.4,"face":"O1"},{"type":"contest","from":2.3,"to":2.7}],"X4":[{"type":"stance","from":0,"to":5.5,"face":"O1"}],
   "O1":[{"type":"celebrate","from":3.0,"to":4.0}]},
 "claims":[{"type":"near","a":"X2","b":"O2","at":"release","max":1.6,"says":"the corner defender stays home"},
           {"type":"near_rim","player":"O1","at":"release","max":1.5,"says":"the baseline is open: finish at the rim"},
           {"type":"open","player":"O1","at":"release","min":1.2,"says":"the baseline is open: finish at the rim"},
           {"type":"order","marks":["drive","stay","screen","release","make"],"says":"drive, no help, layup"}]}
save(A); save(B)

# ---------------- V02 Spain pick-and-roll
sp=[P("O1","O","Ball handler"),P("O2","O","Back-screener (shooter)"),P("O3","O","Spacer, right corner"),
    P("O4","O","Spacer, left corner"),P("O5","O","Ball screener / roller"),
    P("X1","X","On the ball","O1"),P("X2","X","On the back-screener","O2"),P("X3","X","Right corner","O3"),
    P("X4","X","Left corner","O4"),P("X5","X","On the roller (drop)","O5")]
ss={"O1":[0.0,9.0],"O2":[1.6,2.6],"O3":[6.6,1.3],"O4":[-6.6,1.3],"O5":[-2.0,6.4],
    "X1":[0.0,8.1],"X2":[2.0,3.6],"X3":[5.6,2.1],"X4":[-5.6,2.1],"X5":[-1.4,5.6]}
base_legs={"O5":[{"at":0.0,"to":[-0.75,8.1],"speed":4.0}],
   "O1":[{"at":0.75,"via":[[-1.6,9.0],[-2.6,7.6]],"to":[-3.0,6.0],"speed":4.2}],
   "X1":[{"at":1.45,"via":[[-0.9,8.9]],"to":[-2.9,7.6],"speed":3.5}],
   "O2":[{"at":0.2,"to":[-1.0,5.2],"speed":4.0}],
   "X2":[{"at":0.2,"to":[-0.4,5.9],"speed":3.6}],
   "X5":[{"at":0.5,"to":[-1.6,6.0],"speed":1.2}]}
sa={"X3":[{"type":"stance","from":0,"to":5.0,"face":"O1"}],"X4":[{"type":"stance","from":0,"to":5.0,"face":"O1"}],
    "X5":[{"type":"stance","from":0,"to":5.0,"face":"O1"}],"X1":[{"type":"stance","from":0,"to":1.2,"face":"O1"}]}
SA={"id":"spain-a-roll","title":"Spain pick-and-roll — Case A: the back screen frees the roller","duration":5.0,
 "notes":["O5 sets the ball screen, O1 turns the corner to the left.","X5 drops; O2 comes up from the block and back-screens X5.","X2 stays attached to O2: nobody picks up O5 on the roll. Pass, layup."],
 "players":sp,"start":ss,
 "legs":{**base_legs,"O5":base_legs["O5"]+[{"at":1.4,"via":[[0.6,6.6]],"to":[0.4,2.5],"speed":5.5}]},
 "ball":[{"type":"hold","player":"O1","from":0,"to":2.3,"dribble":True},
         {"type":"pass","from":"O1","to":"O5","t0":2.3,"t1":3.0,"style":"chest"},
         {"type":"hold","player":"O5","from":3.0,"to":3.25},
         {"type":"layup","player":"O5","t0":3.25,"t1":3.65,"make":True}],
 "screens":[],
 "marks":{"start":0,"ballscreen":0.85,"roll":1.4,"backscreen":1.7,"pass":2.3,"catch":3.0,"release":3.25,"make":3.65,"end":5.0},
 "actions":{**sa,"O5":[{"type":"screen","from":0.85,"to":1.4,"face":"X1"},{"type":"celebrate","from":3.8,"to":4.8}],
   "O2":[{"type":"screen","from":1.7,"to":5.0,"face":"X5"}],"X2":[{"type":"stance","from":0,"to":5.0,"face":"O2"}]},
 "claims":[{"type":"near","a":"O2","b":"X5","at":"pass","max":1.3,"says":"a second screen, on the big"},
           {"type":"far","a":"X5","b":"O5","at":"catch","min":3.0,"says":"nobody picks up the roller"},
           {"type":"near_rim","player":"O5","at":"release","max":1.5,"says":"easy two at the rim"},
           {"type":"open","player":"O5","at":"release","min":1.2,"says":"easy two at the rim"},
           {"type":"order","marks":["ballscreen","roll","backscreen","pass","catch","release","make"],"says":"ball screen, back screen, roll, pass, layup"}]}
SB={**SA,"id":"spain-b-pop","title":"Spain pick-and-roll — Case B: X2 switches onto the roller, the back-screener pops",
 "notes":["Same spots at 0 s. X2 leaves O2 to wall off the roll.","O2 pops from the back screen to the top of the arc: open three."],
 "legs":{**base_legs,"O5":base_legs["O5"]+[{"at":1.4,"via":[[0.6,6.6]],"to":[1.0,4.6],"speed":5.5}],
   "X2":base_legs["X2"]+[{"at":1.9,"to":[0.2,3.9],"speed":4.0}],
   "O2":base_legs["O2"]+[{"at":2.05,"to":[0.2,8.8],"speed":5.0}]},
 "ball":[{"type":"hold","player":"O1","from":0,"to":2.6,"dribble":True},
         {"type":"pass","from":"O1","to":"O2","t0":2.6,"t1":3.2,"style":"chest"},
         {"type":"hold","player":"O2","from":3.2,"to":3.55},
         {"type":"shot","player":"O2","t0":3.55,"t1":4.65,"make":True}],
 "marks":{"start":0,"ballscreen":0.85,"roll":1.4,"backscreen":1.7,"switch":1.9,"pop":2.05,"pass":2.6,"catch":3.2,"release":3.55,"make":4.65,"end":5.0},
 "actions":{**sa,"O5":[{"type":"screen","from":0.85,"to":1.4,"face":"X1"}],
   "O2":[{"type":"screen","from":1.7,"to":2.0,"face":"X5"},{"type":"celebrate","from":4.7,"to":5.0}],
   "X2":[{"type":"stance","from":0,"to":1.9,"face":"O2"},{"type":"stance","from":2.6,"to":5.0,"face":"O5"}]},
 "claims":[{"type":"near","a":"X2","b":"O5","at":"pass","max":1.4,"says":"X2 jumps the roller"},
           {"type":"far","a":"X2","b":"O2","at":"catch","min":3.5,"says":"the screener is left alone"},
           {"type":"open","player":"O2","at":"release","min":2.0,"says":"he pops for an open three"},
           {"type":"behind_arc","player":"O2","at":"catch","says":"he pops for an open three"},
           {"type":"order","marks":["ballscreen","roll","backscreen","switch","pop","pass","catch","release","make"],"says":"ball screen, back screen, switch, pop, three"}]}
save(SA); save(SB)
