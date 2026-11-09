import json,sys
sys.path.insert(0,'../scratch')
from words import v1,v2,W
M=lambda f,credit,lic,url,**k: dict(src='media/library/'+f,kind='photo',credit=credit,license=lic,sourceUrl=url,**k)
don=M('commons-57151343.jpg','Luka Dončić, 2016 · Javier Mendia García · CC BY 2.0','CC BY 2.0','https://commons.wikimedia.org/wiki/File:Luka_Doncic_2016.jpg',focus=[0.5,0.3])
fener=M('commons-75452218.jpg',"Real Madrid v Fenerbahçe, EuroLeague 2016 (not the 2018 final) · Sakhalinio · CC BY-SA 4.0",'CC BY-SA 4.0','https://commons.wikimedia.org/wiki/File:Fenerbah%C3%A7e_men%27s_basketball_vs_Real_Madrid_Baloncesto_Euroleague_20161201_(6).jpg',focus=[0.5,0.45])
ff14=M('commons-47284302.jpg','EuroLeague Final Four arena, Milan 2014 (not Belgrade) · Savino Paolella · CC BY 2.0','CC BY 2.0','https://commons.wikimedia.org/wiki/File:Forum_Assago_Euroleague_Final_Four_2014.jpg',focus=[0.5,0.5])
hoop=M('commons-141377399.jpg','Basketball hoop, 2023 · Daderot · CC0','CC0','https://commons.wikimedia.org/wiki/File:Basketball_hoop_with_chains_-_Arlington,_MA.jpg',focus=[0.5,0.4])
mb=M('commons-8830791.jpg','EuroLeague Final Four 2005 (generic) · Sportswikiman · CC BY-SA 3.0','CC BY-SA 3.0','https://commons.wikimedia.org/wiki/File:Marcus_Brown_Euroleague_Final_Four_2005.JPG',focus=[0.5,0.4])
bg=lambda m,t: dict(m,treatment=t)
e1=dict(id='2026-11-11-v1',title='Dončić: EuroLeague MVP at 19',style='player',voice='audio/2026-11-11-v1.mp3',words=W(v1),
 display={'Dončić':'Dončić'},emphasis=['youngest','Dončić','third','MVP'],outro={'seconds':1.2},music={'story':'highlight'},
 hook='stat-slam',ending='fact',sfxBudget=2,
 sources=['https://english.sta.si/2516012/doncic-becomes-youngest-ever-euroleague-mvp','https://www.eurohoops.net/en/euroleague/680384/luka-doncic-is-the-final-four-mvp','https://www.cbssports.com/nba/news/nba-draft-prospect-luka-doncic-wins-euroleague-title-final-four-mvp-and-euroleague-mvp-for-real-madrid','Teodosic EuroLeague MVP 2010 (age 23): EuroLeague records','Images: Wikimedia Commons (credits on screen)'],
 scenes=[
 dict(at=0,type='stat',value=19,**{'from':19},countFor=0.01,label='YEARS OLD',second=dict(at='EuroLeague',value='MVP',label='EUROLEAGUE'),bg=bg(don,'duotone'),camera='push-in'),
 dict(at='Belgrade,',type='headline',lines=['BELGRADE','MAY 2018'],accent=[1],bg=bg(ff14,'tint'),layout='low',camera='pull-out',transition='cut'),
 dict(at='Luka',type='media',media=don,camera='push-in',transition='cut',callouts=[dict(at='title',text='CHAMPIONS',tone='gold')],kicker='Real Madrid',sfx=[dict(at='title',name='crowd_cheer',volume=0.8)]),
 dict(at='and is named',type='headline',lines=['FINAL FOUR','MVP, TOO'],accent=[0],bg=bg(fener,'tint'),layout='high',camera='drift',transition='cut'),
 dict(at='He is',type='stat',value=2,**{'from':2},countFor=0.01,label='MVP AWARDS',kicker='Youngest ever',beats=['youngest','award.'],callouts=[dict(at='youngest',text='YOUNGEST EVER',tone='gold')],bg=bg(hoop,'duotone'),layout='low',camera='push-in',transition='cut'),
 dict(at='The previous',type='split',title='AGE AT MVP',left=dict(name='DONČIĆ 2018',media=don,stats=[['Age','19']]),right=dict(name='TEODOSIĆ 2010',stats=[['Age','23']]),winner='left',beats=['previous','Miloš','four','older.'],callouts=[dict(at='Miloš',text='MVP 2010',tone='white'),dict(at='four',text='4 YEARS',tone='gold')],camera='push-in',transition='cut'),
 dict(at='Weeks',type='stat',value=3,**{'from':3},countFor=0.01,prefix='#',label='NBA DRAFT PICK',kicker='June 2018',beats=['third','draft'],callouts=[dict(at='made',text='NBA',tone='white')],bg=bg(don,'tint'),layout='high',camera='pull-out',transition='flash'),
 ],
 social=dict(caption='EuroLeague MVP at 19. Luka Dončić, 2018.',pinnedComment='Dončić was 19 when he won the EuroLeague MVP, four years younger than the previous youngest winner, Miloš Teodosić. Is that the most impressive season by a European teenager?',reply='Real Madrid won the 2018 EuroLeague title in Belgrade, and Dončić was named MVP of the regular season and of the Final Four.',hashtags=['EuroLeague','LukaDoncic','RealMadrid','BasketballHistory','E2A']))
json.dump(e1,open('episodes/2026-11-11-v1.json','w'),ensure_ascii=False,indent=1)

P=lambda t,until=None,**k: dict(t=t,**({'until':until} if until else {}),**k)
c1=dict(title='ELEVATOR SCREEN',
 tracks=[dict(id='O1',side='O',kf=[[5.22,35,26.5]]),
  dict(id='O2',side='O',kf=[[5.22,25,2],[15.2,25,2],[17.3,25,12],[18.8,25,19],[20.7,25,26],[22.4,25,29.5]]),
  dict(id='O4',side='O',kf=[[5.22,21,12],[18.76,21,12],[20.1,23.2,12]]),
  dict(id='O5',side='O',kf=[[5.22,29,12],[18.76,29,12],[20.1,26.8,12]]),
  dict(id='X1',side='X',kf=[[5.22,31.8,24.2]]),
  dict(id='X2',side='X',kf=[[5.22,25,4.5],[15.2,25,4.5],[17.3,25,9.2],[18.7,25,9.6],[23,25,9.6],[25.5,27.5,17]]),
  dict(id='X4',side='X',kf=[[5.22,17.5,14.2],[18.76,17.5,14.2],[20.5,20.5,15.6]]),
  dict(id='X5',side='X',kf=[[5.22,32.5,14.2],[18.76,32.5,14.2],[20.5,29.5,15.6]])],
 ball=[[5.22,35,26.5],[23.14,35,26.5],[24.5,25,29.5],[25.4,25,29.5],[26.0,25,5.25]],
 arrows=[dict(t=15.2,until=23,pts=[[25,3],[25,12],[25,24],[25,28]],kind='move'),
  dict(t=18.76,until=21.8,pts=[[21,12],[23,12]],kind='screen'),dict(t=18.76,until=21.8,pts=[[29,12],[27,12]],kind='screen'),
  dict(t=23.14,until=25,pts=[[34,26.5],[26,29.3]],kind='pass'),dict(t=25.5,pts=[[25,29.3],[25,6.5]],kind='shot')],
 rings=[dict(t=21.3,until=23,at='X2',text='STUCK',color='#FF5A5F'),dict(t=24.8,until=26.2,at='O2',text='OPEN 3')],
 zones=[dict(t=10.9,until=13.8,cx=25,cy=2.3,rx=2.6,ry=1.8,text=''),dict(t=18.9,until=22,cx=25,cy=12,rx=5,ry=2.4,text='DOORS')],
 steps=[[5.22,'Two screeners, a gap'],[10.9,'2 starts in the gap'],[15.0,'2 sprints through'],[18.7,'Doors close'],[21.3,'X2 hits the wall'],[23.1,'Pass: open three']])
c2=dict(title='THE COUNTER',
 tracks=[dict(id='O1',side='O',kf=[[26.3,35,26.5]]),
  dict(id='O2',side='O',kf=[[26.3,25,2],[28.4,25,2],[29.8,25,8],[30.9,25,8.5],[32.3,26.6,7]]),
  dict(id='O4',side='O',kf=[[26.3,21,12]]),dict(id='O5',side='O',kf=[[26.3,29,12]]),
  dict(id='X1',side='X',kf=[[26.3,31.8,24.2]]),
  dict(id='X2',side='X',kf=[[26.3,25,4.5],[28.2,25,4.5],[29.7,25,12.8]]),
  dict(id='X4',side='X',kf=[[26.3,17.5,14.2]]),dict(id='X5',side='X',kf=[[26.3,32.5,14.2]])],
 ball=[[26.3,35,26.5],[31.3,35,26.5],[32.5,26.6,7],[32.9,26.6,7],[33.5,25,5.25]],
 arrows=[dict(t=28.2,until=30.8,pts=[[25,5.5],[25,12.5]],kind='chase'),dict(t=30.9,until=33,pts=[[25,8.5],[26.6,6.8]],kind='move'),
  dict(t=31.3,until=32.6,pts=[[34,26],[27,8]],kind='pass'),dict(t=32.9,pts=[[26.6,7],[25,5.6]],kind='shot')],
 rings=[dict(t=28.3,until=30.2,at='X2',text='AHEAD',color='#FF5A5F'),dict(t=30.8,until=32.4,at='O2',text='READ')],
 zones=[],
 steps=[[26.3,'Defender gets ahead'],[30.8,'Read: slip to the rim']])
e2=dict(id='2026-11-11-v2',title='Elevator screens explained',style='tactical',voice='audio/2026-11-11-v2.mp3',words=W(v2),
 display={},emphasis=['elevator','doors','wall','three','reads','rim'],outro={'seconds':1.2},music={'story':'tactical'},
 hook='photo-line',ending='surprise',sfxBudget=2,
 sources=['Standard coaching literature (FIBA Coaching, USA Basketball coach education)','E2A original diagram','Images: Wikimedia Commons (credits on screen)'],
 scenes=[dict(at=0,type='media',media=ff14,camera='push-in',beats=['shooter','glued']),
  dict(at='You build',type='headline',lines=['THE ELEVATOR','SCREEN'],accent=[1],bg=bg(hoop,'duotone'),camera='push-in',transition='cut'),
  dict(at="Here's",type='court',court=c1,camera='static',transition='cut'),
  dict(at='The defense',type='headline',lines=['THE DEFENCE','HAS AN ANSWER'],accent=[1],bg=bg(mb,'blur'),camera='push-in',transition='cut'),
  dict(at=28.0,type='court',court=c2,camera='static',transition='cut'),
  dict(at='Same',type='headline',lines=['SAME ACTION.','TWO READS.'],accent=[1],bg=bg(mb,'tint'),layout='low',camera='pull-out',transition='cut')],
 social=dict(caption='Elevator screens: the doors close, the shooter is free.',pinnedComment='Elevator screens against a defender who gets ahead of the shooter: slip to the rim, or let him cut it off? Which read is easier to guard?',reply='The two screeners close the gap right after the shooter passes, so his defender hits the wall. If the defender gets ahead, the shooter reads it and cuts back to the rim.',hashtags=['BasketballTactics','BasketballIQ','ElevatorScreen','EuropeanBasketball','E2A']))
json.dump(e2,open('episodes/2026-11-11-v2.json','w'),ensure_ascii=False,indent=1)
