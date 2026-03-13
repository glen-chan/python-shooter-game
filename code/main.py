import pygame
from random import randint, uniform
from os.path import join

#initializes the package
pygame.init()

#constants
#360,640
WINDOWS_WIDTH, WINDOWS_HEIGHT = 400,680

# varible
running = True
meteor_event = pygame.event.custom_type()

class Player(pygame.sprite.Sprite):  
     
    def __init__(self, groups):
        super().__init__(groups)
        self.original_surf = pygame.image.load(join('images','spaceship.png')).convert_alpha()
        self.image = self.original_surf
        self.rect = self.image.get_frect(center = (WINDOWS_WIDTH / 2,WINDOWS_HEIGHT - 50))
        self.direction = pygame.math.Vector2()
        self.speed = 300
        self.lives = 3
        self.death_time =  0
        self.start_time = 0
        '''pygame.time.get_ticks() // 1000'''
        self.invencible = False
        self.invencible_strike = 3  
        self.beam = False      

        # cooldown
        self.can_shoot = True
        self.laser_shoot_time = 0
        self.cooldown_duration = 100
                   
        # mask. This line is not necessary because the collide_mask method creates the mask automaticcally if the sprite does not have a mask attribute
        self.mask = pygame.mask.from_surface(self.image)
        self.mask_surf = self.mask.to_surface() 
        self.mask_surf.set_colorkey((0,0,0))     
        
        # to hide the black pixels from the mask
        # mask_surf.set_colorkey((0,0,0))
        # self.image = mask_surf

    def laser_timer(self):
        # we want to run this only if the player cannot shoot
        if not self.can_shoot:
            # to get the time that has passed since we called pygame.init
            current_time = pygame.time.get_ticks()
            # if the time that has passed since last shoot time is >= the cooldown time, player should be able to shoot again
            if current_time - self.laser_shoot_time >= self.cooldown_duration:
                self.can_shoot = True

    def update(self,dt):
        global scroll
                        
        keys = pygame.key.get_pressed()

        #checking borders         
        if self.rect.right >= WINDOWS_WIDTH:
            self.direction.x =  self.direction.x * -1
            self.rect.right -= 1            
            #print(f"direction x: {self.direction.x}")  
        elif self.rect.left <= 0:
            self.direction.x =  self.direction.x * -1
            self.rect.left += 1
            #print(f"direction x: {self.direction.x}")  
        elif self.rect.bottom >= WINDOWS_HEIGHT:
            self.direction.y =  self.direction.y * -1
            self.rect.bottom -= 1
            #print(f"direction y: {self.direction.y}")
        elif self.rect.top <= 50:
            self.direction.y =  self.direction.y * -1
            self.rect.bottom += 1
            #print(f"direction y: {self.direction.y}")       
        else:
            self.direction.x = int(keys[pygame.K_RIGHT]) - int (keys[pygame.K_LEFT])
            self.direction.y = int(keys[pygame.K_DOWN]) - int (keys[pygame.K_UP])           
  
            
    
        #this part is to normalize the speed in case of diagonal movement  
        self.direction = self.direction.normalize() if self.direction else self.direction
            
        self.rect.center += self.direction * self.speed * dt 
        game.scroll += 0.025 
 

        recent_keys = pygame.key.get_just_pressed()
        recent_released = pygame.key.get_just_released()

        if recent_keys[pygame.K_SPACE] and self.can_shoot:
            # when the player presses the space bar, an instance of the laser is created

            if game.powerup == False:
                # with the position being the midtop position of the player - by default there's only one laser
                Laser(game.laser_surf,self.rect.midtop, (game.all_sprites,game.laser_sprites))
                game.laser_sound.play()
            else:                
                #print(game.powerup_effect)
                # with two lasers
                if game.powerup_effect[-1] == 1:                    
                    Laser(game.laser_surf,self.rect.topleft, (game.all_sprites,game.laser_sprites))
                    Laser(game.laser_surf,self.rect.topright, (game.all_sprites,game.laser_sprites))
                    game.laser_sound.play()
                    self.laser_timer( )                
                # LaserBeam
                elif game.powerup_effect[-1] == 2:                      
                    # for i in range (5):
                        #print(f"Top= {self.rect.top}")                        
                        #Laser(game.laser_surf, game.laser_surf.get_frect(topleft= (self.rect.x, self.rect.top - (i * game.laser_height))).topleft, (game.all_sprites,game.laser_sprites))
                    
                    # mainLaserBeam is going to define the area of contact for the collisions
                    LaserBeam(game.mainLaserBeam_surf,self.rect.midtop, (game.all_sprites,game.mainLaserBeam_sprites))
                    # but this is the one we want the user to really see
                    LaserBeam(game.laserBeam_surf,self.rect.midtop, (game.all_sprites,game.laserBeam_sprites))
                    
                    game.player.beam = True
                    game.beam_sound.play()
                # temporary invencibility
                elif game.powerup_effect[-1] == 3:                     
                     game.player.invencible = True
                     #game.player.original_surf
                     game.player.image = game.player.mask_surf                     
                     Laser(game.laser_surf,self.rect.midtop, (game.all_sprites,game.laser_sprites))
                     game.laser_sound.play()
                # default one laser     
                else: 
                    Laser(game.laser_surf,self.rect.midtop, (game.all_sprites,game.laser_sprites))
                    game.laser_sound.play()
        
        if game.player.invencible_strike == 0:
            game.player.invencible = False
            game.player.image = game.player.original_surf
            game.player.invencible_strike = 3

        if recent_released[pygame.K_SPACE] and game.player.beam == True:
            for laserBeam in game.laserBeam_sprites:
                laserBeam.kill()

            for mainLaserBeam in game.mainLaserBeam_sprites:
                mainLaserBeam.kill()

            game.player.beam = False
      
class Star(pygame.sprite.Sprite):
    def __init__(self, groups,surface):
        super().__init__(groups)
        self.image = surface
        self.rect = self.image.get_frect(center = (randint(0,WINDOWS_WIDTH),randint(0,WINDOWS_HEIGHT)))
           
class Laser(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.image = surf
        # from the laser perspective, we want to place it from the midbottom, in front of the player
        self.rect = self.image.get_frect(midbottom = pos)        

    def update(self, dt):
        # to move the laser: speed per data frame
        self.rect.centery -= 400 * dt

        # to destroy the laser sprite when it is not within the Window
        if self.rect.bottom < 0:
            self.kill()

class LaserBeam(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.image = surf
        # from the laser perspective, we want to place it from the midbottom, in front of the player
        self.rect = self.image.get_frect(midbottom = pos)        

    def update(self, dt):
        # to move the laser: speed per data frame
        # self.rect.centery -= 400 * dt
        self.rect.centerx = game.player.rect.centerx
        self.rect.bottom = game.player.rect.top

        # to destroy the laser sprite when it is not within the Window
        if self.rect.bottom < 0:
            self.kill()

class Meteor(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.image = surf
        self.copy_surf = surf
        self.rect = self.image.get_frect(center = pos)
        self.start_time = pygame.time.get_ticks()
        self.lifetime = 3000
        # to give the meteors a random direction and speed
        self.direction = pygame.Vector2(uniform(-0.5,0.5),1)
        self.speed = randint(200,300)
        
        self.rotation = 0
        self.rotation_speed = randint(40,80)

        self.size = uniform(0.25,1.5)
        self.image = pygame.transform.scale_by(self.image,self.size)
        # to create a mask for the sprite. This line is not necessary because the collide_mask method creates the mask automaticcally if the sprite does not have a mask attribute
        self.mask = pygame.mask.from_surface(self.image)
        self.copy_surf = pygame.transform.scale_by(self.copy_surf,self.size)

    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt
        # to move the meteor down: speed per data frame
        self.rect.centery += self.speed * dt

        # to destroy the meteor after 2 seconds
        current_time = pygame.time.get_ticks()
        
        if current_time - self.start_time >= self.lifetime:
            self.kill()

        # rotation
        self.rotation += self.rotation_speed * dt
        self.image = pygame.transform.rotozoom(self.copy_surf, self.rotation,1)
        # with the last two lines, it works well, but the rotation looks weird because
        # we are overwriting self.image but not the rectangle, to correct thaat:
        self.rect = self.image.get_frect(center = self.rect.center)

class Alien(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.image = surf
        self.copy_surf = surf
        self.rect = self.image.get_frect(center = pos)
        self.start_time = pygame.time.get_ticks()
        self.lifetime = 3000
        # to give the meteors a random direction and speed
        self.direction = pygame.Vector2(uniform(-0.5,0.5),1)
        self.speed = randint(200,300)
       
        self.size = uniform(0.25,1)
        self.image = pygame.transform.scale_by(self.image,self.size)
        # to create a mask for the sprite. This line is not necessary because the collide_mask method creates the mask automaticcally if the sprite does not have a mask attribute
        self.mask = pygame.mask.from_surface(self.image)
        #self.copy_surf = pygame.transform.scale_by(self.copy_surf,self.size)

    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt
        # to move the meteor down: speed per data frame
        self.rect.centery += self.speed * dt

        # to destroy the meteor after 2 seconds
        current_time = pygame.time.get_ticks()
        
        if current_time - self.start_time >= self.lifetime:
            self.kill()

class Extralife(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.image = surf
        self.copy_surf = surf
        self.rect = self.image.get_frect(center = pos)
        self.start_time = pygame.time.get_ticks()
        self.lifetime = 3000
        # to give the powerup a random direction and speed
        self.direction = pygame.Vector2(uniform(-0.5,0.5),1)
        self.speed = randint(200,300)
       
        self.size = uniform(0.2,0.4)
        self.image = pygame.transform.scale_by(self.image,self.size)
        # to create a mask for the sprite. This line is not necessary because the collide_mask method creates the mask automaticcally if the sprite does not have a mask attribute
        self.mask = pygame.mask.from_surface(self.image)
        self.copy_surf = pygame.transform.scale_by(self.copy_surf,self.size)

    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt
        # to move the meteor down: speed per data frame
        self.rect.centery += self.speed * dt

        # to destroy the meteor after 2 seconds
        current_time = pygame.time.get_ticks()
        
        if current_time - self.start_time >= self.lifetime:
            self.kill()

class AnimatedExplosion(pygame.sprite.Sprite):
    def __init__(self, frames, pos, groups):
        super().__init__(groups)
        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_frect(center = pos)
        

    def update(self, dt):
        self.frame_index  += 20 * dt
        # with the line below, there is an animation, but we get an out of index error because it continues increasing indefinitely
        # self.image = self.frames[int(self.frame_index)]
        # to correct that we use the module to obtain the remainder of the index / 20
        # self.image = self.frames[int(self.frame_index) % len (self.frames)]
        # now the problem is that the animation runs indefinitely
        # to correct that:
        # if the index is less than the number of frames, we use the index and if not, we kill the sprite
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
        else:
             self.kill()

class gameOver(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center = pos)
        #self.group = groups
                

    def update(self,groups):        
        global running
                         
        # displays game over image
        game.display_surface.blit(self.image,self.rect)
        
        # displaying want to continue?
        continue_surf = game.font2.render("Continue? Y / N",True,'#ff0055')     
        continue_rect = continue_surf.get_frect(midtop = (WINDOWS_WIDTH / 2, WINDOWS_HEIGHT - 100))     
        game.display_surface.blit(continue_surf,continue_rect)

        keys = pygame.key.get_pressed()

        if keys[pygame.K_n]:
            running = False
        elif keys[pygame.K_y]:
            #print('restart')
            self.kill()
            game.reset_game()

class gameStart(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center = pos)
        #self.group = groups
                

    def update(self,groups):        
        global running
                         
        # displays game over image
        #game.display_surface.blit(self.image,self.rect)
        
        # displaying welcome message
        welcome_surf = game.font.render("Welcome to Piu Piu!",True,"#238f08")     
        welcome_rect = welcome_surf.get_frect(midtop = (WINDOWS_WIDTH / 2, WINDOWS_HEIGHT - 300))     
        game.display_surface.blit(welcome_surf,welcome_rect)

        # displaying instruction message 
        instr_surf = game.font.render("Space key to shoot. Arrows to move",True,"#238f08")     
        instr_rect = instr_surf.get_frect(midtop = (WINDOWS_WIDTH / 2, WINDOWS_HEIGHT - 250))     
        game.display_surface.blit(instr_surf,instr_rect)

        # displaying want to Start?
        start_surf = game.font2.render("Start? Y / N",True,'#ff0055')     
        start_rect = start_surf.get_frect(midtop = (WINDOWS_WIDTH / 2, WINDOWS_HEIGHT - 200))     
        game.display_surface.blit(start_surf,start_rect)

        keys = pygame.key.get_pressed()

        if keys[pygame.K_n]:
            running = False
        elif keys[pygame.K_y]:
            #print('restart')
            self.kill()
            game.reset_game()
            pygame.time.set_timer(meteor_event,game.meteor_frequency)            


class Game(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.set_mode((WINDOWS_WIDTH,WINDOWS_HEIGHT))
        pygame.display.set_caption('Space Shooter')        

        # using vector to define the direction. Parameters are x,y
        # direction = pygame .math.Vector2(0,0)
        # player_speed = 300
        self.clock = pygame.time.Clock()
        self.collision_score = 0
        self.high_score = 1000
        self.scroll = 0
        self.timer = 0
        self.meteor_frequency = 200
        self.powerup = False
        self.powerup_effect = [0]

        # import
        self.bg_surf = pygame.image.load(join('images','deepSpace.jpg')).convert_alpha()
        self.bg_width = self.bg_surf.get_width()
        self.bg_height = self.bg_surf.get_height()

        self.star_surf = pygame.image.load(join('images','RetroStar.png')).convert_alpha()
        self.meteor_surf = pygame.image.load(join('images','Meteorite.png')).convert_alpha()
        self.alien_surf = pygame.image.load(join('images','alien.png')).convert_alpha()
        self.laser_surf = pygame.image.load(join('images','laser.png')).convert_alpha()
        self.laser_height = self.laser_surf.get_height()

        self.heart_surf = pygame.image.load(join('images','heart.png')).convert_alpha()
        self.clock_surf = pygame.image.load(join('images','clock.png')).convert_alpha()
        self.crown_surf = pygame.image.load(join('images','Crown.png')).convert_alpha()
        self.gameOver_surf = pygame.image.load(join('images','gameOver.png')).convert_alpha()        
        self.satellite_surf = pygame.image.load(join ('images','satellite.png')).convert_alpha()
        self.point_surf = pygame.image.load(join ('images','point.png')).convert_alpha()
        self.extralife_surf = pygame.image.load(join('images','life.png')).convert_alpha()
        
        # the laser beam image that the user will see
        self.laserBeam_surf = pygame.image.load(join('images','flare2.png')).convert_alpha()
        # an empty image to define the area of contact for collisions with the beam 
        self.mainLaserBeam_surf = pygame.image.load(join('images','flare4.png')).convert_alpha()

        # Font(font type, font size). font type = None is a default type
        self.font = pygame.font.Font(join('images','Oxanium-Bold.ttf'),20)
        self.font2 = pygame.font.Font(join('images','Oxanium-Bold.ttf'),40)


        # to store the explosion frames in a list
        # we load the image from folder explossion, based on the name of the file (numbered)
        # 21 because there are 21 images in the images/explosion folder
        self.explosion_frames = [pygame.image.load(join('images','explosion',f'{i}.png')).convert_alpha() for i in range (21)]
        # print(explosion_frames)

        '''IMPORTING AUDIO FILES'''

        # laser
        self.laser_sound  = pygame.mixer.Sound(join('audio','laser4.mp3'))
        # to set the volume (float between 0 and 1)
        self.laser_sound.set_volume(0.5)

        # beam
        self.beam_sound  = pygame.mixer.Sound(join('audio','laser9.mp3'))
        self.beam_sound.set_volume(0.5)

        # explosion
        self.explosion_sound  = pygame.mixer.Sound(join('audio','explosion.wav'))
        self.explosion_sound.set_volume(0.05)

        # damage
        self.damage_sound  = pygame.mixer.Sound(join('audio','lowRandom.mp3'))
        #self.damage_sound.set_volume(0.5)

        # background music
        self.game_music  = pygame.mixer.Sound(join('audio','game_music4.mp3'))
        self.game_music.set_volume(0.2)
        self.game_music.play(loops = -1)
        
        # powerup
        self.powerup_sound  = pygame.mixer.Sound(join('audio','powerUp7.mp3'))
        #self.powerup_sound.set_volume(0.4)
        
        # lost
        self.lost_sound  = pygame.mixer.Sound(join('audio','lowDown.mp3'))
        self.lost_sound.set_volume(10.0)

        # it is possible to specify the number of times a sound file is played
        # next line plays the music file 5 times
        # game_music.play(loops = 5)
        # next line plays the music file indefinitely (what we want for the game music )
        # game_music.play(loops = -1)

        ''' creating Sprite groups '''
        # for all sprites
        self.all_sprites  = pygame.sprite.Group()

        # we create another sprites group to manage collisions between the meteor and the player
        self.meteor_sprites = pygame.sprite.Group()

        # we create another sprites group to manage collisions between the alien and the player
        self.alien_sprites = pygame.sprite.Group()

        # we create another sprites group to manage collisions between the extralife and the player
        self.extralife_sprites = pygame.sprite.Group()

        # we create another sprites group to manage collisions between the meteor and the lasers
        self.laser_sprites = pygame.sprite.Group()
        self.laserBeam_sprites = pygame.sprite.Group()  
        self.mainLaserBeam_sprites = pygame.sprite.Group()      
        
        self.player = Player(self.all_sprites)

    def reset_game(self):
        self.clock = pygame.time.Clock()
                           
        self.collision_score = 0
        self.powerup = False

        self.meteor_sprites.empty()
        self.alien_sprites.empty()
        self.extralife_sprites.empty()
        self.all_sprites.empty()
        self.player = Player(self.all_sprites)  
        self.player.start_time = pygame.time.get_ticks() // 1000      
       
    def display_score(self):             

        # to create a surface for the text
        # this will render the text 'text' in red color
        # color can be specified by a common alias, or with a tuple for r,g,b, or with a string in hexadecimal format
        self.score_surf = self.font.render(str(game.collision_score),True,'#ff0055')    
        self.score_rect = self.score_surf.get_frect(midtop = (WINDOWS_WIDTH / 2, 25))

        # adding an image of a crown for the score    
        crown_rect = self.crown_surf.get_frect( midtop=  ((WINDOWS_WIDTH / 2) - 35, 20))
        self.display_surface.blit(self.crown_surf,crown_rect) 
    
        # to draw a rectangle around the score text
        # inflate grows or shrinks the rectangle size
        # move moves the rectangle coordinates
        pygame.draw.rect(self.display_surface,'white',self.score_rect.inflate(70,30).move(-10,-5),5,10)
        
        self.display_surface.blit(self.score_surf,self.score_rect) 

        # displaying a text for the number of lives
        lives_surf = self.font.render(str(self.player.lives),True,'#ff0055')    
        lives_rect = lives_surf.get_frect(midtop = (50, 25))
        self.display_surface.blit(lives_surf,lives_rect) 

        # adding an image of a heart for the number of lives    
        heart_rect = self.heart_surf.get_frect( midtop= (20,20))
        self.display_surface.blit(self.heart_surf,heart_rect) 
        
        # to draw a rectangle around the number of lives
        pygame.draw.rect(self.display_surface,'white',lives_rect.inflate(70,30).move(-10,-5),5,10)


        if self.player.lives == 0:
            # displaying played time until the player died
            time_surf = self.font.render(str(self.player.death_time - self.player.start_time),True,'#ff0055')        
        else:
        # displaying played time
            time_surf = self.font.render(str((pygame.time.get_ticks() // 1000) - self.player.start_time),True,'#ff0055')
            
        time_rect = time_surf.get_frect(midtop = (WINDOWS_WIDTH - 50, 25))
        self.display_surface.blit(time_surf,time_rect) 

        # adding an image of a clock for the time    
        clock_rect = self.clock_surf.get_frect( midtop= (WINDOWS_WIDTH - 80,20))
        self.display_surface.blit(self.clock_surf,clock_rect) 

        # to draw a rectangle around the time
        pygame.draw.rect(self.display_surface,'white',time_rect.inflate(70,30).move(-10,-5),5,10)

    def collisions(self):
        # check for collisions between player and meteor
        # spritecollide(single sprite, group of sprites, dokill). If dokill is true the sprites from the second argument that collide with the first argument will be destroyed
        # it returns a list of the elements from the group of sprites that have collided with the single sprite
        # print(pygame.sprite.spritecollide(player,meteor_sprites,True))

        # collision meteor and player, alien and the player or extralife and player
        collision_sprites = pygame.sprite.spritecollide(self.player,self.meteor_sprites,True, pygame.sprite.collide_mask)
        collision_sprites += pygame.sprite.spritecollide(self.player,self.alien_sprites,True, pygame.sprite.collide_mask)
        #collision_sprites += pygame.sprite.spritecollide(self.player,self.extralife_sprites,True, pygame.sprite.collide_mask)
        #print(collision_sprites) 
        if collision_sprites:        
            if self.player.lives > 0:
                game.damage_sound.play()
                self.collition_time =  pygame.time.get_ticks() // 1000 

                if self.player.invencible == True:
                    self.player.invencible_strike -= 1                
                else:
                    self.player.lives -= 1
            
            if self.player.lives == 0:
                #game.damage_sound.stop()
                self.player.death_time = pygame.time.get_ticks() // 1000
                self.player.kill()                                          
                gameOver(self.gameOver_surf,(WINDOWS_WIDTH / 2,WINDOWS_HEIGHT / 2), self.all_sprites) 
                self.lost_sound.play(loops=0)                                     


        # collision between laser and meteor or laser and alien or laser and extralife
        for laser in (self.laser_sprites):
            collided_meteors = pygame.sprite. spritecollide(laser, self.meteor_sprites,True)
            collided_aliens = pygame.sprite. spritecollide(laser, self.alien_sprites,True)
            collided_extralife = pygame.sprite. spritecollide(laser, self.extralife_sprites,True)

            if collided_meteors:
                laser.kill()

                #setting the default collision_score
                self.collision_score += 10

                # rewarding the player with an extra life depending on the score
                if self.collision_score > 0 and self.collision_score%self.high_score == 0:
                    self.player.lives += 1
                    self.powerup_sound.play()   

                # creating an instance of the explosion
                AnimatedExplosion(self.explosion_frames, laser.rect.midtop, self.all_sprites)
                self.explosion_sound.play()
                # the previous line could also had been defined in the init method of the animagedExplosion class

            if collided_aliens:
                laser.kill()
                self.collision_score += 10

                if self.collision_score > 0 and self.collision_score%self.high_score == 0:
                    self.player.lives += 1
                    self.powerup_sound.play()
                        
                # creating an instance of the explosion
                AnimatedExplosion(self.explosion_frames, laser.rect.midtop, self.all_sprites)
                self.explosion_sound.play()
                # the previous line could also had been defined in the init method of the animatedExplosion class
                #self.run_powerup()
                self.powerup = True
                self.powerup_sound.play()
                #self.powerup_effect.append(2)
                self.powerup_effect.append(randint(1,4))
                
            # for the moment this is not being used
            if collided_extralife:
                laser.kill()
                AnimatedExplosion(self.explosion_frames, laser.rect.midtop, self.all_sprites)
                #self.powerup = True
                self.powerup_sound.play()
                self.player.lives += 1
  

        # collision between laserBeam and meteor, alien or extralife
        for laserBeam in (self.mainLaserBeam_sprites):
            collided_meteors = pygame.sprite. spritecollide(laserBeam, self.meteor_sprites,True)
            collided_aliens = pygame.sprite. spritecollide(laserBeam, self.alien_sprites,True)
            collided_extralife = pygame.sprite. spritecollide(laserBeam, self.extralife_sprites,True)

            if collided_meteors:
                #laser.kill()
                self.collision_score += 10
                # creating an instance of the explosion
                AnimatedExplosion(self.explosion_frames, laserBeam.rect.midtop, self.all_sprites)
                # self.explosion_sound.play()
                # the previous line could also had been defined in the init method of the animatedExplosion class

            if collided_aliens:
                laserBeam.kill()
                self.collision_score += 10
                # creating an instance of the explosion
                AnimatedExplosion(self.explosion_frames, laserBeam.rect.midtop, self.all_sprites)
                #self.explosion_sound.play()
                # the previous line could also had been defined in the init method of the animatedExplosion class
                #self.run_powerup()
                self.powerup = True
                self.powerup_sound.play()
                self.powerup_effect.append(randint(1,4))
                #self.powerup_effect.append(2)
                

            if collided_extralife:
                #laser.kill()
                AnimatedExplosion(self.explosion_frames, laserBeam.rect.midtop, self.all_sprites)
                #self.powerup = True
                self.powerup_sound.play()
                self.player.lives += 1   

    def run(self):
        global running
        
        # custom events -> meteor event
        # meteor_event = pygame.event.custom_type()
        # creating a timer for the meteor event, each half second
        # pygame.time.set_timer(meteor_event,self.meteor_frequency)
        
        # creating an event type for the alien
        alien_event = pygame.event.custom_type()
        # creating a timer for the alien event, each 5 seconds
        pygame.time.set_timer(alien_event,5000)

        """ # creating an event type for the extra life
        extralife_event = pygame.event.custom_type()
        # creating a timer for the alien event, each 10 seconds
        pygame.time.set_timer(extralife_event,5000) """
        

        while running:
            # defining the frame rate
            # clock.tick(60)n

            # defining the delta time
            dt = self.clock.tick() / 1000
            self.timer = pygame.time.get_ticks() // 1000             

            draw_bg()

            if game.player.start_time == 0:
                gameStart(self.point_surf,(WINDOWS_WIDTH / 2,WINDOWS_HEIGHT / 2), self.all_sprites)

            #event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                # if event.type == pygame.KEYDOWN and event.key  == pygame.K_1:
                #     print('1')
                # if event.type == pygame.MOUSEMOTION:
                #     player_rect.center = event.pos
                if event.type == meteor_event and self.player.lives > 0:
                    # we use two groups: all_sprites for the updates and display and meteor_sprites to classify the sprites
                    Meteor(self.meteor_surf,(randint(0,WINDOWS_WIDTH),randint(-200,-100)),(self.all_sprites,self.meteor_sprites))                    
                
                if event.type == alien_event and self.player.lives > 0:
                    # we use two groups: all_sprites for the updates and display and meteor_sprites to classify the sprites
                    Alien(self.alien_surf,(randint(0,WINDOWS_WIDTH),randint(-200,-100)),(self.all_sprites,self.alien_sprites))

                """ if event.type == extralife_event and self.player.lives > 0 and self.powerup_effect[-1] == 2:
                    # we use two groups: all_sprites for the updates and display and meteor_sprites to classify the sprites
                    Extralife(self.extralife_surf,(randint(0,WINDOWS_WIDTH),randint(-200,-100)),(self.all_sprites,self.extralife_sprites))     """
           

            # calls update on all of the sprites on the group
            self.all_sprites.update(dt)

            # calling collisions method:
            game.collisions()

            # display the score text
            game.display_score()

            # display sprite group
            self.all_sprites.draw(self.display_surface) 

            #draw the game
            pygame.display.update()

            
        # quit the package or deinitializes it
        pygame.quit()       

def draw_bg():    
    #global meteor_event

    for y in range(0, 100, 1): 
        bg_rect = game.bg_surf.get_frect(bottomleft = (0, WINDOWS_HEIGHT - (y * game.bg_height) + game.scroll))   
        game.display_surface.blit(game.bg_surf,bg_rect)    
   


if __name__=="__main__":
    game = Game()
    game.run()

