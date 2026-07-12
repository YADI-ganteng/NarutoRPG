from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.core.window import Window
from kivy.clock import Clock
from random import randint
Window.size=(800,480)
class GameWidget(Widget):
    def __init__(self,**k):
        super().__init__(**k)
        self.p={"x":400,"y":240,"hp":500,"mhp":500,"cp":200,"gold":1000,"lv":1,"kl":0,"sp":5}
        self.en=[{"x":randint(50,750),"y":randint(50,430),"hp":100,"al":True} for i in range(10)]
        self.it=[{"x":randint(100,700),"y":randint(100,380),"c":False} for _ in range(10)]
        self.ks=set()
        Window.bind(on_key_down=lambda w,k,*_:self.ks.add(k))
        Window.bind(on_key_up=lambda w,k,*_:self.ks.discard(k))
        Clock.schedule_interval(self.up,1/60)
    def atk(self):
        for e in self.en:
            if not e["al"]:continue
            if abs(self.p["x"]-e["x"])<80:e["hp"]-=40
            if e["hp"]<=0:e["al"]=False;self.p["kl"]+=1;break
    def up(self,dt):
        if 275 in self.ks:self.p["x"]+=self.p["sp"]
        if 276 in self.ks:self.p["x"]-=self.p["sp"]
        if 273 in self.ks:self.p["y"]+=self.p["sp"]
        if 274 in self.ks:self.p["y"]-=self.p["sp"]
        if 293 in self.ks:self.atk()
        self.p["x"]=max(20,min(780,self.p["x"]));self.p["y"]=max(20,min(460,self.p["y"]))
        for i in self.it:
            if not i["c"] and abs(self.p["x"]-i["x"])<25:i["c"]=True;self.p["gold"]+=100
        self.draw()
    def draw(self):
        self.canvas.clear()
        with self.canvas:
            Color(0.1,0.1,0.2);Rectangle(pos=(0,0),size=(800,480))
            Color(0.2,0.5,0.2);Rectangle(pos=(0,0),size=(800,80))
            for i in self.it:
                if not i["c"]:Color(1,1,0);Ellipse(pos=(i["x"]-8,i["y"]-8),size=(16,16))
            for e in self.en:
                if not e["al"]:continue
                Color(0.8,0.2,0.2);Rectangle(pos=(e["x"]-12,e["y"]-16),size=(24,32))
            Color(1,0.4,0.2);Rectangle(pos=(self.p["x"]-12,self.p["y"]-20),size=(24,36))
class NarutoApp(App):
    def build(self):
        l=BoxLayout(orientation="vertical")
        self.hud=Label(text="Naruto RPG",size_hint=(1,0.1),color=(1,1,1,1))
        self.g=GameWidget()
        l.add_widget(self.hud);l.add_widget(self.g)
        btn=Button(text="ATTACK",size_hint=(1,0.15),background_color=(1,0.2,0.2,1))
        btn.bind(on_press=lambda x:self.g.atk())
        l.add_widget(btn)
        Clock.schedule_interval(lambda dt:self.upd(),0.2)
        return l
    def upd(self):
        p=self.g.p
        self.hud.text=f'HP {int(p["hp"])} | CP {int(p["cp"])} | GOLD {p["gold"]} | KILLS {p["kl"]}'
if __name__=="__main__":NarutoApp().run()
