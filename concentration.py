from kivy.config import Config
Config.set('graphics', 'width', '480') # Change resolution here, this is the resolution of old phones
Config.set('graphics', 'height', '800') 
Config.set('graphics', 'resizable', False) # prevent user from changing the size of the window
from kivy.uix.screenmanager import ScreenManager, Screen # to transverse between windows
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout # general layout
from kivy.uix.gridlayout import GridLayout # for game layout
from kivy.uix.button import Button # most important library
from kivy.uix.label import Label # label for all the texts
from kivy.app import App # main app class
from kivy.core.window import Window # to change window background color
from kivy.core.audio import SoundLoader # load sound
from kivy.uix.image import Image # load images
from kivy.uix.popup import Popup # For game win window
from kivy.uix.behaviors.compoundselection import CompoundSelectionBehavior # For selection box in game
from kivy.uix.behaviors import FocusBehavior # For selection box in game
import random # to use the shuffle() function to change the order of the game button objects
from libdw import sm # to use the state machine class

gameLevel = [1] # global variable for the current level of the game, defaults at level 1 (easy)
gameDiff = {1: (4, 8), 2: (6, 18), 3: (8, 32), 4: (10, 50), 5: (12, 72), 6: (14, 98)} # level 1 is 4x4 grid. thus 16 grids. thus need 8 pairs. level 2 6x6, 36 grids so 18 pairs. ETC...
Window.clearcolor = (1, 1, 1, 1) # Change background to white
mute = [False] # mute list to keep track whether user wants to mute the game

# Start screen manager. Over here are buttons linked to different functions
class StartScreen(Screen):
    def __init__(self, **kwargs):
        Screen.__init__(self, **kwargs)
        self.layout = BoxLayout(orientation='vertical')
        self.layout.add_widget(Image(source='icons/title.gif')) # add title gif
        self.button = [] # Save all the button in a list so that i can change their properties later
        self.button.append(Button(text='START', font_size=30, on_press=self.change_to_game, halign='center', valign='middle'))
        self.button.append(Button(text='HOW TO PLAY?', font_size=30, on_press=self.change_to_howtoplay, halign='center', valign='middle'))
        self.button.append(Button(text='QUIT', font_size=30, on_press=self.quit_app, halign='center', valign='middle'))
        self.button.append(Button(background_normal='icons/unmute.jpg', on_press=self.change_to_mute, size_hint=(.2,1)))
        self.muteLabel = Label(text='unmuted',color=[0, 0, 0, 1], halign='center', valign='bottom', size_hint=(.2,.4))
        self.columnLayout = BoxLayout(orientation='vertical') # create the layout. top half is the title. bottom half is the buttons
        for i in range(3): # add all the buttons to a normal layout
            self.columnLayout.add_widget(self.button[i])
        self.columnLayout.add_widget(self.muteLabel)
        self.columnLayout.add_widget(self.button[3])
        self.layout.add_widget(self.columnLayout)
        self.add_widget(self.layout) # add the buttons to the box layout
        self.bgm = SoundLoader.load('sounds/bgm.wav') # load music
        self.bgm.loop = True # loop background music
        self.bgm.play()
        self.bgm.volume = 0.3 # so that it is not so loud and distracting

    def change_to_game(self, value):
        self.manager.transition.direction = 'left'
        self.manager.current = 'level'

    def change_to_howtoplay(self, value):
        self.manager.transition.direction = 'right'
        self.manager.current = 'howtoplay'

    def change_to_mute(self, value): # Function to mute or not mute the background music
        if self.bgm.state == 'play': 
            self.bgm.stop()
            self.button[3].background_normal = 'icons/mute.jpg' # reference button 3 which is mute/unmute button
            self.muteLabel.text = 'muted'
            mute[0] = True
        else: 
            self.bgm.play()
            self.button[3].background_normal = 'icons/unmute.jpg'
            self.muteLabel.text = 'unmuted'
            mute[0] = False

    def quit_app(self, value):
        self.bgm.stop()
        App.get_running_app().stop()
        Window.close()

# STATE MACHINE is used here as a inner class
# How to play screen in the game. This is to explain how to play the game to the user. 
class HowToPlayScreen(Screen):
    def __init__(self, **kwargs):
        Screen.__init__(self, **kwargs)
        self.images = [] # for the tutorial
        for i in range(1,7):
            self.images.append('icons/step'+str(i)+'.png') # store the location of the images that is for the tutorial
        self.layout = BoxLayout(orientation='vertical')
        self.topBar = BoxLayout(orientation='horizontal', size_hint=(1,.1))
        self.topBarLeftButton = Button(text='BACK', font_size=20, on_press=self.left, halign='center', valign='middle', size_hint=(.2,1))
        self.topBarRightButton = Button(text='NEXT', font_size=20, on_press=self.right, halign='center', valign='middle', size_hint=(.2,1))
        self.topBarLabel = Label(text="Step: 1/6",color=(0,0,0,1), font_size=44, halign='center', valign='middle', size_hint=(.6,1))
        self.topBar.add_widget(self.topBarLeftButton)
        self.topBar.add_widget(self.topBarLabel)
        self.topBar.add_widget(self.topBarRightButton)  
        self.layout.add_widget(self.topBar)
        self.currentImage = Image(source=self.images[0], size_hint=(1,.6))
        self.layout.add_widget(self.currentImage)
        self.intructionLabel = Label(text='Select the "START" button to start the game!\nYou can mute the app if it is too loud!',color=(0,0,0,1), font_size=20, halign='center', valign='middle', size_hint=(1,.2))
        self.layout.add_widget(self.intructionLabel)
        self.layout.add_widget(Button(text='Back to Menu', font_size=20, on_press=self.change_to_startscreen, halign='center', valign='middle', size_hint=(1,.1)))
        self.add_widget(self.layout)
        self.state = self.TutorialSM() # create the state machine object
        self.state.start() # start the state machine object

    def left(self, value):
        var = self.state.step(-1) # reduce the step by 1 when going back, get the appropriate state and message
        self.intructionLabel.text = var[1]
        self.currentImage.source = self.images[var[0]-1]
        self.topBarLabel.text = 'Step: '+ str(var[0])+'/6'
    
    def right(self, value):
        var = self.state.step(1) # increa the step by 1 when going back, get the appropriate state and message
        self.intructionLabel.text = var[1]
        self.currentImage.source = self.images[var[0]-1]
        self.topBarLabel.text = 'Step: '+ str(var[0])+'/6'

    def change_to_startscreen(self, value):
        self.manager.transition.direction = 'left'
        self.manager.current = 'startscreen'

    # STATE MACHINE USED HERE!!! Inner class :) To be only use within this 'how to play' screen
    class TutorialSM(sm.SM):
        def __init__(self):
            self.start_state = 1
            self.message = [] # to store the approriate messages to display in the comment box
            self.message.append('Select the "START" button to start the game!\nYou can mute the app if it is too loud!')
            self.message.append('Select the appropriate level for your skills!')
            self.message.append('Step 1: Select two buttons in the grid\nStep 2: Then press select to confirm choices!')
            self.message.append('If selection is wrong, you can view the\nselected two boxes image and their \ncorresponding button number!')
            self.message.append('If selection is correct, the corresponding buttons\nwill show the images!\nYou can continue to select two buttons and\nopen them! Do it till you WIN!')
            self.message.append('This is what it will look like when you WIN!\nBest of luck and have fun!')

        def get_next_values(self, state, inp):
            if state > 1 and state < 6: 
                nextstate = state + inp
            elif state == 1: # when state is 1 need to check if it is going back, if it is then need to change to state 6
                if inp == 1: 
                    nextstate = state + inp
                else: 
                    nextstate = 6
            elif state == 6: # same logic as if state is at 1 originally
                if inp == 1: 
                    nextstate = 1
                else: 
                    nextstate = state + inp
            output = nextstate, self.message[nextstate - 1] # i want to return the step number it is in and the message
            return nextstate, output # change the current state and then return the step number and the appropriate message

# Game screen class. This is the game screen of the app. User will play the game here.
class Level(Screen):
    def __init__(self, **kwargs):
        Screen.__init__(self, **kwargs)
        self.layout = BoxLayout(orientation='vertical')
        self.gameLayout = BoxLayout(orientation='vertical')
        self.gameLayout1 = BoxLayout(orientation='vertical')
        self.layout.add_widget(self.gameLayout)
        self.button = [] # Save all the button in a list so that i can change their properties later
        self.button.append(Button(text='EASY', font_size=30, on_press=self.startGameE, halign='center', valign='middle'))
        self.button.append(Button(text='MEDIUM', font_size=30, on_press=self.startGameM, halign='center', valign='middle'))
        self.button.append(Button(text='HARD', font_size=30, on_press=self.startGameH, halign='center', valign='middle'))
        self.button.append(Button(text='YOU ARE INSANE!!!!!', font_size=30, on_press=self.startGameINSANE, halign='center', valign='middle'))
        self.button.append(Button(text='LEGENDARY!!!!!', font_size=30, on_press=self.startGameINSANE2, halign='center', valign='middle'))
        self.button.append(Button(text='DONT EVEN TRY...', font_size=30, on_press=self.startGameLegend, halign='center', valign='middle'))
        for i in range(6): # add all the buttons to a normal layout
            self.layout.add_widget(self.button[i])
        self.layout.add_widget(self.gameLayout1)
        self.add_widget(self.layout)
    
    def change_to_load(self):
        self.manager.transition.direction = 'left'
        self.manager.current = 'load'

    def startGameE(self,value):
        gameLevel[0] = 1 # change the global list to the level that is selected
        self.change_to_load()

    def startGameM(self,value):
        gameLevel[0] = 2
        self.change_to_load()

    def startGameH(self,value):
        gameLevel[0] = 3
        self.change_to_load()

    def startGameINSANE(self,value):
        gameLevel[0] = 4
        self.change_to_load()

    def startGameINSANE2(self,value):
        gameLevel[0] = 5
        self.change_to_load()

    def startGameLegend(self,value):
        gameLevel[0] = 6
        self.change_to_load()

# Loading screen in case the game window take too long to launch due to loading the icons for the button
class LoadingScreen(Screen): 
    def __init__(self, **kwargs):
        Screen.__init__(self, **kwargs)
        self.add_widget(Label(text='LOADING\nPLEASE BE PATIENT!',color=(0,0,0,1), font_size=44, halign='center', valign='middle'))

    def on_enter(self):
        self.manager.transition.direction = 'left'
        self.manager.current = 'game'

# Game screen class. This is the game screen of the app. User will play the game here.
class GameScreen(Screen):
    win = SoundLoader.load('sounds/win.wav') # class variable, so that any functions inside this class can play these sound effects
    wrong = SoundLoader.load('sounds/wrong.wav') 
    correct = SoundLoader.load('sounds/correct.wav') 
    def __init__(self, **kwargs):
        Screen.__init__(self, **kwargs)
        self.mainLayout = BoxLayout(orientation='vertical')
        self.layout = BoxLayout(orientation='vertical', size_hint=(1, 0.1))
        self.gameLayout = BoxLayout(orientation='vertical', size_hint=(1, 0.6))
        self.score = 0
        self.gameL = gameDiff[gameLevel[0]][1]
        self.scoreLabel = Label(text='Pairs Found: '+str(self.score)+'/'+str(self.gameL), color=(0,0,0,1), font_size=50, size_hint=(1,.2))
        self.layout.add_widget(self.scoreLabel)
        self.commentMain = BoxLayout(orientation='vertical', size_hint=(1, .3))
        self.commentLayout = BoxLayout(orientation='horizontal', size_hint=(1, .2))
        self.ok = Button(text='Select!', on_press=self.okay, halign='center', valign='middle', size_hint=(.2,1))
        self.commentsLabel = Label(text='Select Two Boxes Then Press THIS -->', color=(0,0,0,1), font_size=20, size_hint=(.8,1), halign='center', valign='middle')
        self.commentLayout.add_widget(self.commentsLabel)
        self.commentLayout.add_widget(self.ok)
        self.previousLabel1 = Label(text='------>\nPrevious\n1\n------>', color=(0,0,0,1), font_size=20, halign='center', valign='middle')
        self.previousLabelP1 = Image()
        self.previousLabel2 = Label(text='------>\nPrevious\n2\n------>', color=(0,0,0,1), font_size=20, halign='center', valign='middle')
        self.previousLabelP2 = Image()
        self.previousl = BoxLayout(orientation='horizontal', size_hint=(1,.7))
        self.previousl.add_widget(self.previousLabel1)
        self.previousl.add_widget(self.previousLabelP1)
        self.previousl.add_widget(self.previousLabel2)
        self.previousl.add_widget(self.previousLabelP2)
        self.returnButton = BoxLayout(orientation='vertical', size_hint=(1, 0.8))
        self.returnButton.add_widget(self.previousl)
        self.returnButton.add_widget(Button(text='End Game!', on_press=self.change_to_startscreen, halign='center', valign='middle', size_hint=(.3,.3)))
        self.commentMain.add_widget(self.commentLayout)
        self.commentMain.add_widget(self.returnButton)
        self.mainLayout.add_widget(self.layout)
        self.mainLayout.add_widget(self.gameLayout)
        self.mainLayout.add_widget(self.commentMain)
        self.add_widget(self.mainLayout)  ### not writing .KV file, results in this huge mess to layout things...

    def on_pre_enter(self): # before entering, will be stuck at the loading screen when actually loading
        self.muted = mute[0] # check if user muted the system. will not play any sound effect if it is muted
        self.previousLabel1.text = '------>\nPrevious\n1\n------>'
        self.previousLabelP1.source = ''
        self.previousLabel2.text = '------>\nPrevious\n2\n------>'
        self.previousLabelP2.source = ''
        self.gameL = gameDiff[gameLevel[0]][1] # get the number of pairs the user needs to find. taken from global dict with tuple inside
        self.numberGrid = gameDiff[gameLevel[0]][0] # get the number of rows and cols. rows == cols. so just one number in the global dict
        self.commentsLabel.text = 'Select Two Boxes Then Press THIS -->'
        self.scoreLabel.text = 'Pairs Found: '+str(self.score)+'/'+str(self.gameL)
        # using another subclass of selectable grid. if 4x4 grid, col and rows should be set accordingly
        self.grid = SelectableGrid(cols=self.numberGrid, rows=self.numberGrid, touch_multiselect=True, multiselect=True) 
        # create a Button list (button object, 0 wrong /1 for correct, photo number ID use to check if same image, photo path)
        self.buttonList = []
        for i in range(1, self.gameL+1): # add 1 image to 1 button list (1 to half number of grid) e.g. easy level: 8 pairs. add 8 photos
            buttonSmallList = []
            buttonSmallList.append(Button()) # add button object as first of the list
            buttonSmallList.append(0) # initialize sceond variable in list as 0 for wrong first
            buttonSmallList.append(i) # then add the ID number of the button
            buttonSmallList.append('gamebuttons/'+str(i)+'.jpg') # add the source of the photo
            self.buttonList.append(buttonSmallList)
        for i in range(self.gameL+1, self.gameL*2+1): # add duplicated number. e.g. easy level: add another 8 of the same photos as previous for loop
            buttonSmallList = []
            buttonSmallList.append(Button())
            buttonSmallList.append(0)
            buttonSmallList.append(i-self.gameL) # should be same as the previous list
            buttonSmallList.append('gamebuttons/'+str(i-self.gameL)+'.jpg')
            self.buttonList.append(buttonSmallList) 
        random.shuffle(self.buttonList) # to randonmize the list and where the buttons are
        for i in range(1, self.numberGrid**2+1):
            self.buttonList[i-1][0].text='{0}'.format(i) # change the button text to display correct sequence. e.g. easy level 1-16
            self.grid.add_widget(self.buttonList[i-1][0]) # add the buttons to the selectable grid.
        self.gameLayout.add_widget(self.grid)
        
    def change_to_startscreen(self, value):
        self.score = 0 # reset the scoring
        self.gameLayout.remove_widget(self.grid) # remove every single widget in the game layout widget. so that when user come back in with different level, it will change to that
        self.manager.transition.direction = 'right'
        self.manager.current = 'startscreen'

    def okay(self, value): # game logic
        if len(SelectableGrid.selection) == 2: # check from the public class variable in the selectablegrid class how many is selected. will be 2 or less
            self.commentsLabel.text = 'Checking if it is the same!' # if checking takes too long, will not happen most of the time
            check = [] # function variable to save the location of the buttons that are pressed with their orignal list with all their elements such as whether they were opened before and such
            for i in SelectableGrid.selection: # get the buttons that are pressed
                for j in self.buttonList: # go through the whole buttonlist created in the pre_enter function
                    if i in j: # if button location is in the j
                        check.append(j) # add to check list to check if same
            self.grid.deselect_node(check[0][0]) # auto deselect the buttons so that user can straightaway press other buttons
            self.grid.deselect_node(check[1][0])
            if check[0][1]==0 and check[1][1]==0: # check if both boxes are unopened
                self.previousLabel1.text = '------>\nPrevious\n'+check[0][0].text+'\n------>' # display button number selected
                self.previousLabelP1.source = check[0][3] # display the selected boxes corresponding images
                self.previousLabel2.text = '------>\nPrevious\n'+check[1][0].text+'\n------>'
                self.previousLabelP2.source = check[1][3]
                if check[0][2] == check[1][2]: # if they are have the same image ID
                    self.commentsLabel.text = 'SAME! Congrats!' 
                    if not self.muted: self.correct.play() # play correct sound
                    for i in range(2): # go through both the buttons that are correct
                        check[i][0].background_normal=check[i][3] # show the images of the buttons that are correct in the selectable grids
                        check[i][0].text = '' # remove the texts
                        check[i][1] = 1 # check the logic in the button list to 'correct/opened'
                    self.score+=1 # add the score 
                    self.scoreLabel.text = 'Pairs Found: '+str(self.score)+'/'+str(self.gameL) # update the scoreboard label
                else: # if it is not the same
                    if not self.muted: self.wrong.play()
                    self.commentsLabel.text = 'NOT SAME! Choose Again!'
                if self.score == self.gameL: # win condition! check if user won the game
                    self.commentsLabel.text = 'YOU WIN! Press End Game Button,\nTo Return To Start Screen!'
                    if not self.muted: self.win.play()
                    WinPopup.open(self) # use the popup class to inform user has won!
            else: # check if user selected boxes that are opened
                count = 0
                for i in self.buttonList: # check if user keeps opening boxes even if they have won
                    if i[1] == 0:
                        count += 1
                if count != 0: # if it is not 0 means that there are boxes still unopen!
                    self.commentsLabel.text = 'DO NOT CHOOSE OPENED BOXES!'
                    if not self.muted: self.wrong.play()
                else: # if 0 means all boxes opened and won, then tell user to stop fooling around and end the game!
                    self.commentsLabel.text = 'Stop selecting!\nPress "END GAME" button to quit!'
        else: # if user never select two boxes
            self.commentsLabel.text = 'SELECT TWO BOXES PLEASE!'
            if not self.muted: self.wrong.play()

# subclass to make selectable grids for the game layout. Did some modification from -> Source: https://kivy.org/doc/stable/api-kivy.uix.behaviors.compoundselection.html
class SelectableGrid(FocusBehavior, CompoundSelectionBehavior, GridLayout):
    selection = []
    def add_widget(self, widget):
        # Override the adding of widgets so we can bind and catch their *on_touch_down* events
        widget.bind(on_touch_down=self.button_touch_down, on_touch_up=self.button_touch_up)
        return super(SelectableGrid, self).add_widget(widget)

    def button_touch_down(self, button, touch):
        # Use collision detection to select buttons when the touch occurs within their area
        if button.collide_point(*touch.pos):
            self.select_with_touch(button, touch)

    def button_touch_up(self, button, touch):
        # Use collision detection to de-select buttons when the touch occurs outside their area and *touch_multiselect* is not True
        if not (button.collide_point(*touch.pos) or self.touch_multiselect):
            self.deselect_node(button)

    def select_node(self, node):
        node.background_color = (1, 0, 0, 1)
        return super(SelectableGrid, self).select_node(node) #super(SelectableGrid, self).deselect_node(node)
    
    def deselect_node(self, node): # will be used by another class to automatically deslect the node
        node.background_color = (1, 1, 1, 1)
        super(SelectableGrid, self).deselect_node(node)

    def on_selected_nodes(self, gird, nodes):
        if len(nodes) > 2: # prevent selection from reaching above 2
            nodes[-1].background_color = (1, 1, 1, 1) # change the background color 
            super(SelectableGrid,self).deselect_node(nodes[-1]) # deslect the node for them
        SelectableGrid.selection = nodes # change the public class list to the currently selected nodes to be accessed by another class (gamescreen class)

# Winning popup when user win
class WinPopup(Popup):
    def open(self):
        self.dismiss_btn = Button(text='YAY! I WIN!')
        self.popup = Popup(title='YOU HAVE WON!', content = self.dismiss_btn, size_hint = (1, .15), title_align='center')
        self.dismiss_btn.bind(on_press =lambda *args: self.popup.dismiss())
        self.popup.open()

# Main class which game is started from
class ConcGame(App):
    def build(self):
        screen_m = ScreenManager() # Create a screen manager class to store all the different screens
        screen_m.add_widget(StartScreen(name='startscreen')) # There are three screen states: 1. Start Screen, 2. How to play? and 3. Game
        screen_m.add_widget(HowToPlayScreen(name='howtoplay')) # How to play screen. Uses STATE MACHINE to function
        screen_m.add_widget(Level(name='level')) # For user to select the level they want to play
        screen_m.add_widget(LoadingScreen(name='load')) # Loading screen in case the game window take too long to load
        screen_m.add_widget(GameScreen(name='game')) # the game screen
        screen_m.current = 'startscreen' # Set first screen to the start screen
        return screen_m # Start the screen manager returning it to .run()

ConcGame().run() # Run game function