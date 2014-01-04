import pygame
import pygwrap
import stats
import rpgmenu
import image
import items

EL_NAME = ( "Light", "Heavy", "Severe" )
def encumberance_desc( pc, show_ceiling=True ):
    """Return a string describing this PC's encumberance level."""
    mass = sum( i.mass for i in pc.inventory )
    ec = pc.get_encumberance_ceilings()
    el = pc.encumberance_level()
    if show_ceiling:
        return "{0}.{1}/{2}.{3}lbs {4}".format( mass//10, mass%10, ec[el]//10, ec[el]%10, EL_NAME[el] )
    else:
        return "{0}.{1}lbs {2}".format( mass//10, mass%10, EL_NAME[el] )

class CharacterSheet( pygame.Rect ):
    # Note that the display will be larger than this, because the border is
    # drawn outside. Consider this measurement the safe area and the border the bleed.
    WIDTH = 320
    HEIGHT = 450
    BODY_Y = 70
    RIGHT_COLUMN = 155

    MISC_STATS = ( stats.AWARENESS, stats.CRITICAL_HIT, stats.DISARM_TRAPS, \
        stats.HOLY_SIGN, stats.KUNG_FU, stats.NATURAL_DEFENSE, stats.STEALTH, \
        stats.RESIST_SLASHING, stats.RESIST_PIERCING, stats.RESIST_CRUSHING, \
        stats.RESIST_ACID, stats.RESIST_COLD, stats.RESIST_FIRE, stats.RESIST_LIGHTNING, \
        stats.RESIST_POISON, stats.RESIST_WATER, stats.RESIST_WIND, \
        stats.RESIST_LUNAR, stats.RESIST_SOLAR, stats.RESIST_ATOMIC )

    def __init__( self, pc, x=0, y=0, screen = None, camp = None ):
        if screen:
            x = screen.get_width() // 2 - self.WIDTH
            y = screen.get_height() // 2 - self.HEIGHT // 2 + 32
        super(CharacterSheet, self).__init__(x,y,self.WIDTH,self.HEIGHT)
        self.pc = pc
        self.camp = camp
        self.regenerate_avatar()

    def regenerate_avatar( self ):
        mybmp = pygame.Surface( (54 , 54) )
        mybmp.fill((0,0,255))
        mybmp.set_colorkey((0,0,255),pygame.RLEACCEL)
        myimg = self.pc.generate_avatar()
        myimg.render( mybmp, frame=self.pc.FRAME )
        self.img = pygame.transform.scale2x( mybmp )

    def just_print( self, screen, x, y, text1, text2, width=120 ):
        """Do proper justification for stat line at x,y."""
        pygwrap.draw_text( screen, pygwrap.SMALLFONT, text1, pygame.Rect( x, y, width, 20 ), justify = -1 )
        pygwrap.draw_text( screen, pygwrap.SMALLFONT, text2, pygame.Rect( x, y, width, 20 ), justify = 1 )

    def render( self, screen ):
        pygwrap.default_border.render( screen , self )

        # Header avatar
        if self.img:
            screen.blit(self.img , (self.x-20,self.y-20) )

        # Header info- name and level/gender/race/class
        y = self.y + 6
        pygwrap.draw_text( screen, pygwrap.BIGFONT, self.pc.name, pygame.Rect( self.x+64, y, self.width-64, pygwrap.BIGFONT.get_linesize() ), justify = 0, color=(240,240,240) )
        y += pygwrap.BIGFONT.get_linesize()
        pygwrap.draw_text( screen, pygwrap.SMALLFONT, self.pc.desc(), pygame.Rect( self.x+64, y, self.width-64, pygwrap.SMALLFONT.get_linesize() ), justify = 0 )
        y += pygwrap.SMALLFONT.get_linesize()
        pygwrap.draw_text( screen, pygwrap.SMALLFONT, "XP: "+str(self.pc.xp)+"/"+str(self.pc.xp_for_next_level()), pygame.Rect( self.x+64, y, self.width-64, pygwrap.SMALLFONT.get_linesize() ), justify = 0 )

        # Column 1 - Basic info
        y = self.y + self.BODY_Y
        for s in stats.PRIMARY_STATS:
            self.just_print( screen, self.x, y, s.name+":", str( max( self.pc.get_stat(s) , 1 ) ) )
            y += pygwrap.SMALLFONT.get_linesize()

        y += pygwrap.SMALLFONT.get_linesize()

        self.just_print( screen, self.x, y, "HP:", str( self.pc.current_hp() ) + "/" + str( self.pc.max_hp() ) )
        y += pygwrap.SMALLFONT.get_linesize()
        self.just_print( screen, self.x, y, "MP:", str( self.pc.current_mp() ) + "/" + str( self.pc.max_mp() ) )
        y += pygwrap.SMALLFONT.get_linesize() * 2
        if self.camp:
            self.just_print( screen, self.x, y, "Gold:", str( self.camp.gold ) )
        else:
            self.just_print( screen, self.x, y, "Gold:", "0" )
        y += pygwrap.SMALLFONT.get_linesize()
        self.just_print( screen, self.x, y, "Encumberance:", "" )
        y += pygwrap.SMALLFONT.get_linesize()
        self.just_print( screen, self.x, y, "", encumberance_desc( self.pc, False ), width=135 )


        # Column 2 - skills
        y = self.y + self.BODY_Y
        self.just_print( screen, self.x+self.RIGHT_COLUMN, y, "Melee:", str(self.pc.get_stat(stats.PHYSICAL_ATTACK)+self.pc.get_stat_bonus(stats.STRENGTH))+"%" )
        y += pygwrap.SMALLFONT.get_linesize()
        self.just_print( screen, self.x+self.RIGHT_COLUMN, y, "Missile:", str(self.pc.get_stat(stats.PHYSICAL_ATTACK)+self.pc.get_stat_bonus(stats.REFLEXES))+"%" )
        y += pygwrap.SMALLFONT.get_linesize()
        self.just_print( screen, self.x+self.RIGHT_COLUMN, y, "Defence:", str(self.pc.get_defense())+"%" )
        y += pygwrap.SMALLFONT.get_linesize()
        self.just_print( screen, self.x+self.RIGHT_COLUMN, y, "Magic:", str(self.pc.get_stat(stats.MAGIC_ATTACK)+self.pc.get_stat_bonus(stats.INTELLIGENCE))+"%" )
        y += pygwrap.SMALLFONT.get_linesize()
        self.just_print( screen, self.x+self.RIGHT_COLUMN, y, "Aura:", str(self.pc.get_stat(stats.MAGIC_DEFENSE)+self.pc.get_stat_bonus(stats.PIETY))+"%" )
        y += pygwrap.SMALLFONT.get_linesize() * 2

        for s in self.MISC_STATS:
            # Stealth gets a bit of special treatment here.
            if s is stats.STEALTH:
                if self.pc.can_use_stealth():
                    sv = self.pc.get_stat(s) + self.pc.get_stat_bonus( s.default_bonus )
                    self.just_print( screen, self.x+self.RIGHT_COLUMN, y, s.name+":", str(sv)+"%", width=160 )
                    y += pygwrap.SMALLFONT.get_linesize()
            elif s is stats.HOLY_SIGN:
                if self.pc.can_use_holy_sign():
                    sv = self.pc.get_stat(s) + self.pc.get_stat_bonus( s.default_bonus )
                    self.just_print( screen, self.x+self.RIGHT_COLUMN, y, s.name+":", str(sv)+"%", width=160 )
                    y += pygwrap.SMALLFONT.get_linesize()
            else:
                sv = self.pc.get_stat(s)
                if sv:
                    if s.default_bonus:
                        sv += self.pc.get_stat_bonus( s.default_bonus )
                    self.just_print( screen, self.x+self.RIGHT_COLUMN, y, s.name+":", str(sv)+"%", width=160 )
                    y += pygwrap.SMALLFONT.get_linesize()

class MenuRedrawer( object ):
    def __init__( self , border_rect = None, backdrop = "bg_wests_stonewall5.png", charsheet = None, screen = None, caption = None ):
        self.backdrop = image.Image( backdrop )
        self.counter = 0
        self.charsheet = charsheet
        if screen and not border_rect:
            border_rect = pygame.Rect( screen.get_width()//2 + 64, screen.get_height()//2 - CharacterSheet.HEIGHT//2 + 32, CharacterSheet.WIDTH - 64, CharacterSheet.HEIGHT )
        self.rect = border_rect
        if screen:
            self.caption_rect = pygame.Rect( screen.get_width()//2 - 240, screen.get_height()//2 - CharacterSheet.HEIGHT//2 - 46, 480, pygwrap.BIGFONT.get_linesize() )
        else:
            self.caption_rect = None
        self.caption = caption

    def __call__( self , screen ):
        self.backdrop.tile( screen , ( self.counter * 5 , self.counter ) )
        if self.charsheet:
            self.charsheet.render( screen )
        if self.rect:
            pygwrap.default_border.render( screen , self.rect )
        if self.caption and self.caption_rect:
            pygwrap.default_border.render( screen , self.caption_rect )
            pygwrap.draw_text( screen, pygwrap.BIGFONT, self.caption, self.caption_rect, justify = 0 )
        self.counter += 4

class PartySelectRedrawer( object ):
    def __init__( self , border_rect = None, backdrop = "bg_wests_stonewall5.png", menu=None, charsheets=None, screen = None, caption=None ):
        self.backdrop = image.Image( backdrop )
        self.counter = 0
        self.menu = menu
        self.charsheets = charsheets
        if screen and not border_rect:
            border_rect = pygame.Rect( screen.get_width()//2 + 64, screen.get_height()//2 - CharacterSheet.HEIGHT//2 + 32, CharacterSheet.WIDTH - 64, CharacterSheet.HEIGHT )
        self.rect = border_rect
        if screen:
            self.caption_rect = pygame.Rect( screen.get_width()//2 - 240, screen.get_height()//2 - CharacterSheet.HEIGHT//2 - 46, 480, pygwrap.BIGFONT.get_linesize() )
        else:
            self.caption_rect = None
        self.caption = caption

    def __call__( self , screen ):
        self.backdrop.tile( screen , ( self.counter * 5 , self.counter ) )
        if self.menu and self.charsheets:
            self.charsheets[ self.menu.items[ self.menu.selected_item ].value ].render( screen )
        if self.rect:
            pygwrap.default_border.render( screen , self.rect )
        if self.caption and self.caption_rect:
            pygwrap.default_border.render( screen , self.caption_rect )
            pygwrap.draw_text( screen, pygwrap.BIGFONT, self.caption, self.caption_rect, justify = 0 )
        self.counter += 4

def display_item_info( screen, it, myrect ):
    """Use the screen to display "it" in myrect."""
    y = myrect.y
    pygwrap.draw_text( screen, pygwrap.BIGFONT, str( it ), pygame.Rect( myrect.x, y, myrect.width, pygwrap.BIGFONT.get_linesize() ), justify = 0, color=(240,240,240) )
    y += pygwrap.BIGFONT.get_linesize()
    myrect = pygame.Rect( myrect.x, y, myrect.width, pygwrap.SMALLFONT.get_linesize() )
    pygwrap.draw_text( screen, pygwrap.SMALLFONT, str( it.cost() ) + " GP", myrect, justify = -1 )
    pygwrap.draw_text( screen, pygwrap.SMALLFONT, str( it.mass // 10 ) + "." + str( it.mass % 10 ) + "lbs", myrect, justify = 1 )
    y += pygwrap.BIGFONT.get_linesize()

    if it.true_desc:
        myimg = pygwrap.render_text(pygwrap.SMALLFONT, it.true_desc, myrect.width, justify = -1 )
        myrect = myimg.get_rect( topleft = ( myrect.x, y ) )
        screen.blit( myimg , myrect )
        y += myrect.height + 6

    msg = it.stat_desc()
    if msg:
        myimg = pygwrap.render_text(pygwrap.ITALICFONT, msg, myrect.width, justify = 0 )
        myrect = myimg.get_rect( topleft = ( myrect.x, y ) )
        screen.blit( myimg , myrect )


class CharacterViewRedrawer( object ):
    # A redrawer for the status/inventory screen.
    def __init__( self , border_rect=None, backdrop="bg_wests_stonewall5.png", menu=None, csheet=None, screen=None, caption=None, predraw=None ):
        self.backdrop = image.Image( backdrop )
        self.counter = 0
        self.csheet = csheet
        if screen and not border_rect:
            border_rect = pygame.Rect( screen.get_width()//2 + 64, screen.get_height()//2 - CharacterSheet.HEIGHT//2 + 32, CharacterSheet.WIDTH - 64, CharacterSheet.HEIGHT )
        self.rect = border_rect
        if screen:
            self.caption_rect = pygame.Rect( screen.get_width()//2 - 240, screen.get_height()//2 - CharacterSheet.HEIGHT//2 - 46, 480, pygwrap.BIGFONT.get_linesize() )
        else:
            self.caption_rect = None
        self.caption = caption
        self.menu = menu
        self.predraw = predraw

    def __call__( self , screen ):
        if self.predraw:
            self.predraw( screen )
        else:
            self.backdrop.tile( screen , ( self.counter * 5 , self.counter ) )
        if self.csheet:
            self.csheet.render( screen )
        if self.rect:
            pygwrap.default_border.render( screen , self.rect )
            if self.menu:
                # Display the item info in the upper display rect.
                it = self.menu.items[ self.menu.selected_item ].value
                if isinstance( it, items.Item ):
                    display_item_info( screen, it, self.rect )
        if self.caption and self.caption_rect:
            pygwrap.default_border.render( screen , self.caption_rect )
            pygwrap.draw_text( screen, pygwrap.BIGFONT, self.caption, self.caption_rect, justify = 0 )
        self.counter += 4

class InvExchangeRedrawer( object ):
    # A redrawer for the picking up items/getting items from container screen.
    def __init__( self , backdrop="bg_wests_stonewall5.png", menu=None, off_menu=None, screen=None, caption=None, predraw=None, pc=None ):
        self.backdrop = image.Image( backdrop )
        self.counter = 0
        if screen:
            self.rect1 = pygame.Rect( screen.get_width() // 2 - CharacterSheet.WIDTH, screen.get_height() // 2 - CharacterSheet.HEIGHT // 2 + 32, CharacterSheet.WIDTH, CharacterSheet.HEIGHT )
            self.rect2 = pygame.Rect( screen.get_width()//2 + 64, screen.get_height()//2 - CharacterSheet.HEIGHT//2 + 32, CharacterSheet.WIDTH - 64, CharacterSheet.HEIGHT )
            self.caption_rect = pygame.Rect( screen.get_width()//2 - 240, screen.get_height()//2 - CharacterSheet.HEIGHT//2 - 46, 480, pygwrap.BIGFONT.get_linesize() )
        else:
            self.rect1 = None
            self.rect2 = None
            self.caption_rect = None
        self.caption = caption
        self.menu = menu
        self.off_menu = off_menu
        self.predraw = predraw
        self.pc = pc
    def __call__( self , screen ):
        if self.predraw:
            self.predraw( screen )
        else:
            self.backdrop.tile( screen , ( self.counter * 5 , self.counter ) )
        if self.rect1:
            pygwrap.default_border.render( screen , self.rect1 )
            if self.pc:
                pygwrap.draw_text( screen, pygwrap.BIGFONT, str( self.pc ), self.rect1, justify=0, color=(240,240,240) )
                myrect = pygame.Rect( self.rect1.x, self.rect1.y + pygwrap.BIGFONT.get_linesize(), self.rect1.width, 32 )
                pygwrap.draw_text( screen, pygwrap.ITALICFONT, "carrying " + encumberance_desc( self.pc ), myrect, justify=0 )

        if self.rect2:
            pygwrap.default_border.render( screen , self.rect2 )
            if self.menu:
                # Display the item info in the upper display rect.
                it = self.menu.items[ self.menu.selected_item ].value
                if isinstance( it, items.Item ):
                    display_item_info( screen, it, self.rect2 )
        if self.caption and self.caption_rect:
            pygwrap.default_border.render( screen , self.caption_rect )
            pygwrap.draw_text( screen, pygwrap.BIGFONT, self.caption, self.caption_rect, justify = 0 )
        if self.off_menu:
            self.off_menu.render( do_extras=False )
        self.counter += 4



class LeftMenu( rpgmenu.Menu ):
    # This menu appears in what is normally the character sheet area.
    def __init__( self, screen, predraw = None, border=None ):
        x = screen.get_width() // 2 - CharacterSheet.WIDTH
        y = screen.get_height() // 2 - CharacterSheet.HEIGHT // 2 + 40 + pygwrap.BIGFONT.get_linesize() * 2
        super(LeftMenu, self).__init__(screen,x,y,CharacterSheet.WIDTH,CharacterSheet.HEIGHT - pygwrap.BIGFONT.get_linesize() * 2, border=border)
        self.predraw = predraw




class RightMenu( rpgmenu.Menu ):
    # This is, obviously, the menu that appears to the right of the character sheet.
    def __init__( self, screen, charsheet = None, predraw = None, border=None, add_desc=True ):
        x = screen.get_width()//2 + 64
        y = screen.get_height()//2 - CharacterSheet.HEIGHT//2 + 232
        w = CharacterSheet.WIDTH - 64
        h = CharacterSheet.HEIGHT - 200
        if not add_desc:
            y += -200
            h += 200
        super(RightMenu, self).__init__(screen,x,y,w,h,border=border)
        if add_desc:
            self.add_desc( x, y-200, w, 180, justify=0 )
        if not predraw:
            predraw = MenuRedrawer( border_rect = pygame.Rect( x , y-200, w, CharacterSheet.HEIGHT ), charsheet = charsheet )
        self.predraw = predraw

