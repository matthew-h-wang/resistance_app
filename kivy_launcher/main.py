from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.scatter import Scatter
from kivy.uix.scatterlayout import ScatterLayout
from kivy.properties import ListProperty, ObjectProperty, NumericProperty, BooleanProperty, StringProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from random import shuffle

team_counts = {5:(3,2),6:(4,2),7:(4,3),8:(5,3),9:(6,3),10:(6,4)}
mission_counts = {5:(2,3,2,3,3),6:(2,3,3,3,4),7:(2,3,3,4,4),8:(3,4,4,5,5),9:(3,4,4,5,5),10:(3,4,4,5,5)}
mission_counts_str = {5:'2, 3, 2, 3, 3  ',6:'2, 3, 3, 3, 4  ',7:'2, 3, 3, 4*, 4',8:'3, 4, 4, 5*, 5',9:'3, 4, 4, 5*, 5',10:'3, 4, 4, 5*, 5'}
mission_star = {5:(False,False,False,False,False),6:(False,False,False,False,False),7:(False,False,False,True,False),8:(False,False,False,True,False),9:(False,False,False,True,False),10:(False,False,False,True,False)}

class NumPlayersScreen(Screen):
	controller = ObjectProperty(None)

	numplayers = NumericProperty(7)
	r_count = NumericProperty(0)
	s_count = NumericProperty(0)
	m_counts_str = StringProperty('')


class PlayerIDScreen(Screen):
	controller = ObjectProperty(None)

	numplayers = NumericProperty(0)
	r_count = NumericProperty(0)
	s_count = NumericProperty(0)

	playerstack = ObjectProperty(None)
	startbutton = None

	def populate_playerstack(self):
		if self.startbutton != None :
			self.remove_widget(self.startbutton)
			self.startbutton = None
		self.playerstack.clear_widgets()

#clean this part up some?
		tc = team_counts[self.numplayers]
		identities = []
		for i in range(0, tc[0]) :
			identities.append(True)
		for i in range(0, tc[1]) :
			identities.append(False)
		shuffle(identities)

		for x in range(0, self.numplayers) :
			button = PlayerIDButton(text= 'Player ' + str(x+1), identity=identities[x])
			self.playerstack.add_widget(button)
			button.bind(on_press = self.goto_playernamescreen)
			button.bind(on_disabled = self.check_allplayersdone)

	def goto_playernamescreen(self, instance) :
		self.manager.transition.direction = 'left' 
		self.manager.current = 'PlayerNameScreen' 
		self.manager.current_screen.current_name.text = instance.text
		self.manager.current_screen.current_ID = instance.identity 
		self.manager.current_screen.current_button = instance

	def check_allplayersdone(self, *args) :
		if self.startbutton != None :
			return

		for child in self.playerstack.children:
			if not child.disabled :
				return
		
		self.startbutton = StartGameButton(id='startbutton')
		self.add_widget(self.startbutton)
		self.startbutton.bind(on_press = self.controller.start_game)

	def on_enter(self, *args):
		self.check_allplayersdone(self)

class StartGameButton(Button):
	pass

class PlayerIDButton(Button):
	identity = BooleanProperty(True)

class PlayerSelectButton(ToggleButton):
	pass

class PlayerNameScreen(Screen):
	controller = ObjectProperty(None)

	current_name = ObjectProperty('')
	current_ID = BooleanProperty('')
	current_button = ObjectProperty('')
	id_button = ObjectProperty('')

	def on_pre_leave(self, *args):
		self.current_button.text = self.current_name.text



class MissionSelectScreen(Screen):
	controller = ObjectProperty(None)
	gobutton = ObjectProperty(None)
	mission_num = NumericProperty(1)
	mission_count = NumericProperty(0)
	selected_count = NumericProperty(0)

	playerstack = ObjectProperty(None);

	def on_pre_enter(self):
		self.gobutton.disabled = True

	def on_enter(self, *args):
		self.mission_count = self.controller.m_counts[self.mission_num - 1]
		self.update_selected_count()

	def update_selected_count(self, *args):
		print('counting')
		c = 0
		for button in self.playerstack.children :
			if button.state == 'down' :
				c += 1
		self.selected_count = c
		if c == self.mission_count :
			self.gobutton.disabled = False
		else :
			self.gobutton.disabled = True

	def start_mission(self) :
		on_mission = []
		for button in self.playerstack.children :
			if button.state == 'down' :
				on_mission.append(button.text) 

		self.manager.transition.direction = 'left' 
		self.manager.current = 'MissionChoiceScreen' 
		self.manager.current_screen.playerstack = on_mission

class MissionChoiceScreen(Screen):
	controller = ObjectProperty(None)

	playerstack = ListProperty([])
	votestack = ListProperty([])

	dragspace = ObjectProperty(None)

	passcard = ObjectProperty(None)
	failcard = ObjectProperty(None)

	playedcards = ListProperty([])

	def on_enter(self, *args):
		self.reset_cards()
		self.votestack = []

	def reset_cards(self):
		print('resetting cards')
		pos = [.25,.75]
		shuffle(pos)
		self.passcard.center_x=self.width * pos.pop()
		self.passcard.center_y=self.height/4
		self.failcard.center_x=self.width * pos.pop()
		self.failcard.center_y=self.height/4

	def add_pass(self):
		if not self.passcard.collide_widget(self.dragspace) :
			return
		self.playerstack.pop()
		self.votestack.append(True)
		self.reset_cards()
		if not self.playerstack:
			self.manager.transition.direction = 'left' 
			self.manager.current = 'MissionResultScreen' 
			self.manager.current_screen.votestack = self.votestack
	
	def add_fail(self):
		if not self.failcard.collide_widget(self.dragspace) :
			return
		self.playerstack.pop()
		self.votestack.append(False)
		self.reset_cards()
		if not self.playerstack:
			self.manager.transition.direction = 'left' 
			self.manager.current = 'MissionResultScreen' 
			self.manager.current_screen.votestack = self.votestack

class MissionResultScreen(Screen):
	controller = ObjectProperty(None)
	cardspace = ObjectProperty(None)

	mission_num = NumericProperty(1)

	votestack = ListProperty([])
	revealed = BooleanProperty(False)
	revealbutton = ObjectProperty(None)

	def on_pre_enter(self):
		self.cardspace.clear_widgets() 
		self.revealed = False
		

	def reveal(self, *args):
		if self.revealed:
			self.cardspace.clear_widgets() 
			self.manager.transition.direction = 'left' 
			print(str(self.controller.s_wins) + ' to '+ str(self.controller.r_wins))
			if self.controller.s_wins == 3 or self.controller.r_wins == 3:
				self.manager.current = 'GameResultScreen' 
			else :
				self.manager.current = 'MissionSelectScreen' 
				self.manager.current_screen.mission_num += 1
			return

		shuffle(self.votestack)
		c = 1.0
		t = len(self.votestack) + 1
		failcount = 0
		for vote in self.votestack :
			if vote == True :
				self.cardspace.add_widget(ResultLabel(text='PASS',color=(0,1,0,1)))
			else :
				self.cardspace.add_widget(ResultLabel(text='FAIL',color=(1,0,0,1)))				
				failcount += 1
			c += 1

		if failcount >= (2 if mission_star[self.controller.n_players][self.mission_num - 1] else 1) :
			self.controller.s_wins += 1
		else :
			self.controller.r_wins += 1
		self.revealed = True

class PassCard(Scatter):
	pass

class FailCard(Scatter):
	pass

class ResultLabel(Label):
	pass
class GameResultScreen(Screen):
	controller = ObjectProperty(None)
	resulttext = StringProperty('')

class ResistanceGame(BoxLayout):
	n_players = NumericProperty(0)
	n_resistance = NumericProperty(0)
	n_spies = NumericProperty(0)
	m_counts = ()
	m_counts_str = StringProperty('')
	m_star = ()

	player_names = ListProperty([])
	player_ids = ListProperty([])

	r_wins = NumericProperty(0)
	s_wins = NumericProperty(0)

	def on_n_players(self, instance, value,*args):
		self.n_resistance, self.n_spies = team_counts[value] 
		self.m_counts= mission_counts[value]
		self.m_counts_str = mission_counts_str[value]
		self.m_star = mission_star[value]

	def start_game(self, *args) :
		idscreen =	self.manager.get_screen('PlayerIDScreen')
		selectscreen = self.manager.get_screen('MissionSelectScreen')
		self.player_names = []
		self.player_ids = []
		self.r_wins = 0
		self.s_wins = 0
		for button in idscreen.playerstack.children :
			self.player_names.insert(0,button.text)
			self.player_ids.insert(0,button.identity)
		
		selectscreen.playerstack.clear_widgets()

		for name in self.player_names :
			button = PlayerSelectButton(text= name)
			selectscreen.playerstack.add_widget(button)
			button.bind(on_press=selectscreen.update_selected_count)

		self.manager.transition.direction = 'left' 
		self.manager.current = 'MissionSelectScreen'
		self.manager.current_screen.mission_num = 1
		self.manager.current_screen.mission_count = self.m_counts[0]


	def go_back(self):
		self.manager.transition.direction = 'right' 
		if self.manager.current == 'PlayerIDScreen':
			self.manager.current = 'NumPlayersScreen'
		elif self.manager.current == 'PlayerNameScreen':
			self.manager.current = 'PlayerIDScreen'
		elif self.manager.current == 'MissionChoiceScreen':
			self.manager.current = 'MissionSelectScreen'
		elif self.manager.current == 'MissionResultScreen' and  not self.manager.current_screen.revealed :
			self.manager.current = 'MissionSelectScreen'
		elif self.manager.current == 'GameResultScreen':
			self.manager.current = 'NumPlayersScreen'
			self.manager.get_screen('PlayerIDScreen').populate_playerstack()

class ResistanceApp(App):
	pass
#		def build(self):

#			sm = ScreenManager()

			#sm.add_widget(NumPlayersScreen(name='NumPlayersScreen'))
			#sm.add_widget(PlayerIDScreen(name='PlayerIDScreen'))	
			#sm.current = 'NumPlayersScreen'
#			return sm


if __name__ == '__main__':
	ResistanceApp().run()