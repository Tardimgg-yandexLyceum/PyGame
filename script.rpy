# Вы можете расположить сценарий своей игры в этом файле.

# Определение персонажей игры.
define losyash = Character('Лосяш', color="#f2a300", image="лосяш")
define pin = Character('Пин', color="#4d4d4d", image="пин")
define sovuny = Character('Совунья', color="#805796", image="совунья")
define ii = Character('[iiname]', color="#e6e6e6", image="ии")
define krosh = Character('Крош', color="#92e1e6", image="крош")
define ejik = Character('Ежик', color="#c95278", image="ежик")
define nusha = Character('Нюша', color="#f7c7d1", image="нюша")
define barash = Character('Бараш', color="#ffdcfe", image="бараш")
define karych = Character('Кар-Карыч', color="#406db9", image="карыч")
define kopatych = Character('Копатыч', color="#fa7a45", image="копатыч")

define n = Character(None, kind=nvl)

define otnkrosh = False
define otnbarash = False
define otnkarych = False
define otnsovuny = False
define raketa = False
define otn = 0

define audio.babochka = "music/бабочка.mp3"
define audio.kosmos = "music/космос.mp3"
define audio.barash_i_nusha = "music/бараш и нюша.mp3"
define audio.muskarych = "music/карыч.mp3"
define audio.muskopatych = "music/копатыч.mp3"
define audio.krosh_i_ejik = "music/крош и ежик.mp3"
define audio.naushnay_tema = "music/научная тема.mp3"
define audio.neytralnay = "music/нейтральная.mp3"
define audio.pin_prosnulsy = "music/пин проснулся.mp3"
define audio.sibir = "music/сибирь.mp3"
define audio.stihi = "music/стихи.mp3"
define audio.stolknovenie_sovuny = "music/столкновение совуньи.mp3"
define audio.strany = "music/страны.mp3"
define audio.fantiki = "music/фантики.mp3"
define audio.horoshiy_konec = "music/хороший конец.mp3"
define audio.ot_vinta = "music/От винта.mp3"


 

init python:


    class View:
        def __init__(self, position, displayable, min_size=(0, 0), **kwargs):
            if "box_view" in kwargs:
                kwargs["box_view"].addView(self)
            self._x = position[0]
            self._y = position[1]
            self._displayable = displayable
            self._min_size = (min_size[0], min_size[1])
            self._size = self._min_size

        def render(self, r, width, height, st, at):
            render_view = renpy.render(self._displayable, width, height, st, at)
            size = render_view.get_size()
            self._size = (max(size[0], self._min_size[0]), max(size[1], self._min_size[1]))
            r.blit(render_view, (self._x, self._y))

        def event(self, position, **kwargs):
            return False

        def get_displayable(self):
            return self._displayable

        def set_position(self, position):
            self._x, self._y = position[0], position[1]

        def get_position(self):
            return (self._x, self._y)

        def get_size(self):
            return self._size

        def exit(self):
            pass


    class ButtonView(View):

        def __init__(self, view, **kwargs):
            if "box_view" in kwargs:
                kwargs["box_view"].addView(self)
            self._root_view = view

        def event(self, position, **kwargs):
            if "recursive_event" in kwargs:
                self._root_view.event(position, kwargs=kwargs)
            x, y = self.get_position()
            size = self.get_size()
            return (x + size[0]) > position[0] > x and (y + size[1]) > position[1] > y

        def render(self, r, width, height, st, at):
            self._root_view.render(r, width, height, st, at)

        def get_position(self):
            return self._root_view.get_position()

        def get_view(self):
            return self._root_view

        def set_position(self, position):
            self._root_view.set_position(position)

        def get_size(self):
            return self._root_view.get_size()

        def exit(self):
            self._root_view.exit()


    class EditText(View):

        def __init__(self, start_text, position, max_symbol=float("inf"), **kwargs):
            if "box_view" in kwargs:
                kwargs["box_view"].addView(self)
            self._start_text = start_text
            self._text = self._start_text
            self._cursor = "|"
            self._max_symbol = max_symbol
            self._text_view = Text("".join(self._text))
            self._position = position
            super(EditText, self).__init__(self._position, self._text_view, (max_symbol * 19.4, 0))
            self._text_button = ButtonView(self)
            self._update_cursor = EditText.UpdateCursor(1, self._render_add_function, self._render_remove_function, self)
            self._update_cursor.setDaemon(True)
            self._update_cursor.start()
            self._is_active = False

        def _render_add_function(self, parent):
            self._text_view.set_text(self._text + self._cursor)

        def _render_remove_function(self, parent):
            self._text_view.set_text(self._text)

        def set_position(self, position):
            super(EditText, self).set_position(position)
            self._position = position

        def get_position(self):
            return self._position

        def on_active(self):
            self._is_active = True
            self._update_cursor.resume()

        def off_active(self):
            self._is_active = False
            self._update_cursor.pause()

        def get_text(self):
            return self._text

        def event(self, position, symbol=None, backspace=False, **kwargs):
            if "position" in kwargs:
                position = kwargs["position"]
            if "symbol" in kwargs:
                symbol = kwargs["symbol"]
            if "backspace" in kwargs:
                backspace = kwargs["backspace"]
            if symbol != None:
                if self._is_active:
                    self._update_cursor.pause()
                    if backspace:
                        if len(self._text) > len(self._start_text):
                            self._text = self._text[:-1]
                            self._text_view.set_text(self._text)
                    elif len(self._text) < self._max_symbol:
                        self._text += symbol
                        self._text_view.set_text(self._text)
                    self._update_cursor.resume()
            elif self._text_button.event(position):
                self._update_cursor.resume()
                self.on_active()
            else:
                self._update_cursor.pause()
                self.off_active()

        def exit(self):
            self._update_cursor.exit()

        import threading

        class UpdateCursor(threading.Thread):

            import time

            def __init__(self, update_time, render_add_function, render_remove_function, parent):
                import pygame, threading

                super(EditText.UpdateCursor, self).__init__(self)
                self._render_add_function = render_add_function
                self._render_remove_function = render_remove_function
                self._update_time = update_time
                self._is_add_function = 0
                self._is_work = True
                self._parent = parent
                self._clock = pygame.time.Clock()
                self._event = threading.Event()

            def run(self):
                while self._is_work:
                    if self._is_add_function:
                        self._event.wait()
                        self._render_add_function(self._parent)
                    else:
                        self._render_remove_function(self._parent)
                        self._event.wait()
                    self._is_add_function = not self._is_add_function
                    self._clock.tick(2)

            def exit(self):
                self.resume()
                self._is_work = False
                super(UpdateCursor, self).exit()

            def pause(self):
                self._event.clear()

            def resume(self):
                self._event.set()


    class FieldView(View):
        def __init__(self, position, root_view, *views, **kwargs):
            if "box_view" in kwargs:
                kwargs["box_view"].addView(self)
            self._child_view = []
            self._child_start_position = []
            self._view = root_view
            self._position = position
            super(FieldView, self).__init__(self._position, self._view)
            for value in views:
                self._child_start_position.append(value.get_position())
                self._child_view.append(value)
            self._set_child_position()

        def _set_child_position(self):
            for i in range(len(self._child_view)):
                self._child_view[i].set_position((self._child_start_position[i][0] + self._position[0],
                                                  self._child_start_position[i][1] + self._position[1]))

        def render(self, r, width, height, st, at):
            super(FieldView, self).render(r, width, height, st, at)
            for value in self._child_view:
                value.render(r, width, height, st, at)

        def exit(self):
            super(FieldView, self).exit()
            for value in self._child_view:
                value.exit()

        def event(self, position, **kwargs):
            answer = []
            for value in self._child_view:
                answer.append(value.event(position, kwargs=kwargs))
            return answer

        def get_views(self):
            return self._child_view

        def set_position(self, position):
            self._position = position
            super(FieldView, self).set_position(position)
            self._set_child_position()

        def get_position(self):
            return self._position

        def get_size(self):
            return self._size


    class FlyView(View):

        def __init__(self, view, speed=5, **kwargs):
            if "box_view" in kwargs:
                kwargs["box_view"].addView(self)
            self._root_view = view
            self._start_x, self._start_y = self._root_view.get_position()
            self._current_x = float(self._start_x)
            self._current_y = float(self._start_y)
            self._k_x = 1.0
            self._k_y = 1.0
            self._size = (0, 0)
            self._speed = speed
            self._stop = True
            self._last_coordinates = None
            self._end_position = None

        def render(self, r, width, height, st, at):
            if (not self._stop):
                self._move()
            self._root_view.render(r, width, height, st, at)

        def get_end_position(self):
            return self._end_position

        def is_in_start(self):
            return abs(self._current_y - self._start_y) < self._speed

        def is_in_end(self):
            return self._stop and not self.is_in_start()

        def get_view(self):
            return self._root_view

        def _move(self):
            if abs(self._current_y - self._last_coordinates[1]) < self._speed and abs(
                    self._current_x - self._last_coordinates[0]) < self._speed:
                self._stop = True
            else:
                self._current_x += self._k_x
                self._current_y += self._k_y
            self._root_view.set_position((self._current_x, self._current_y))

        def event(self, position, **kwargs):
            return self._root_view.event(position, kwargs=kwargs)

        def get_position(self):
            return self._root_view.get_position()

        def set_position(self, position):
            self._current_x, self._current_y = position
            self._stop = True
            self._root_view.set_position(position)

        def get_size(self):
            return self._root_view.get_size()

        def get_view(self):
            return self._root_view

        def exit(self):
            self._root_view.exit()

        def fly(self, last_coordinates):
            if last_coordinates != None:
                self._end_position = last_coordinates
            if (self._stop):
                if last_coordinates == None:
                    last_coordinates = (self._start_x, self._start_y)
                self._last_coordinates = last_coordinates
                delta_x = abs(self._current_x - self._last_coordinates[0])
                delta_y = abs(self._current_y - self._last_coordinates[1])
                if delta_x > delta_y:
                    self._k_x = 1
                    self._k_y = float(abs(self._current_y - self._last_coordinates[1])) / abs(
                        self._current_x - self._last_coordinates[0])
                elif delta_x < delta_y:
                    self._k_x = float(abs(self._current_x - self._last_coordinates[0])) / abs(
                        self._current_y - self._last_coordinates[1])
                    self._k_y = 1
                else:
                    self._k_x = 1
                    self._k_y = 1
                self._k_x *= 1 if self._current_x < self._last_coordinates[0] else -1
                self._k_y *= 1 if self._current_y < self._last_coordinates[1] else -1
                self._k_x *= self._speed
                self._k_y *= self._speed
                self._stop = False
                self._move()
                return True

            return False


    class BoxView:

        def __init__(self):
            self._views = []

        def addView(self, view):
            self._views.append(view)

        def render(self, r, width, height, st, at):
            for value in self._views:
                value.render(r, width, height, st, at)

        def exit(self):
            for value in self._views:
                value.exit()

# Игра начинается здесь:
label start:

    scene ночь без ракеты
 
    play music kosmos

    show лосяш телескоп
    with dissolve

    losyash "Как же интересно наблюдать за ночным небом!"

    scene ночь с ракетой

    show лосяш телескоп

    losyash "Погодите-ка, что это такое? Это же падающая звезда!"

    scene ночь без ракеты

    show лосяш телескоп

    losyash "Она упала в лесу, надо срочно её найти!"


label raketa:

    scene упавшая ракета
    with fade

    show лосяш ступор

    losyash "Феноменально, это же космическая ракета! Нужно срочно попасть внутрь!"

    show лосяш серьезный
    with Dissolve(.2)
    losyash "Хм, один я, наверно, не открою дверь, нужно позвать Пина!"

    stop music fadeout 1


label dom_pina:

    play music ot_vinta

    scene сон пина
    with fade


    pin "ОТ, ОТ, ОТ ВИНТА!!!"

    pause(5)

    show лосяш восторженный
    with dissolve

    losyash "Пин, ракета, ракета!!!"

    play music pin_prosnulsy

    scene дом пина
    with fade

    show лосяш восторженный1

    show пин сонный1

    losyash "Друг мой холодный, вставайте, я нашёл странную ракету в лесу!"

    pin "Оох, не надо было на ночь читать комиксы! {w=3} Ладно, идём..."


label pustay_raketa:

    scene упавшая ракета
    with fade

    show пин сонный

    show лосяш восторженный2

    pin "*зевает* Ну, обычная ракета, похожа на мою, ничего особенного."

    losyash "Но погодите, друг мой скептический. Раньше эта дверь была закрыта!"

    hide лосяш восторженный2
    with dissolve

    pause(2)

    show лосяш расстроенный
    with dissolve

    losyash "Не может быть... {w=2} Внутри ничего нет, ракета пуста!"

    pin "Наверное, опять Крош с Ёжиком начудили, Лосяш, не обращай внимания."

    losyash "Нет, здесь явно что-то не так, может, кто-то еще видел что-то странное."

    stop music fadeout 1

label stolknovenie:

    play music stolknovenie_sovuny

    show черный экран
    with fade

    pause(2)

    "...Некоторое время спустя..."

    scene тропинка
    with fade


    show совунья лыжи:
        xalign 0.5 yalign 0.4
        linear 0.5 xalign 0.6 yalign 0.52 zoom 1.3
        linear 0.7 xalign 0.63 yalign 0.9 zoom 2.1

    pause .5

    show иидв with dissolve:
        xalign 0.1 yalign 0.8 
        linear 0.8 xalign 0.7 zoom 1.2

    pause 0.3

    hide совунья лыжи

    hide иидв

    show совунья на лыжах

    show иидв1:
        xalign 0.7 yalign 0.8 zoom 1.2

   

    sovuny "Aaaaa!!!"

    "Неизвестный" "АЙ!"

    show черный экран
    with vpunch

    pause(1)

    scene тропинка
    with fade

    show совунья пришибленная

    sovuny "Вот дела!"

    show лосяш обычный with dissolve

    show пин обычный with dissolve
    
    losyash "Здравствуйте, а вы не видели здесь что-то необычное?"

    sovuny "Еду себе спокойно на лыжах, а тут НЕЧТО выбегает прямо из леса, попадает под лыжи и просто убегает!"

    losyash вопрос "А можно поинтересоваться, куда именно?"

    sovuny "Куда-то в сторону моря, кажется..."

    losyash восторженный2 "Я же говорил, что что-то здесь не так!"

    pin "Йа-йа! Действительно. Скорее туда!"

    stop music fadeout 1


label krosh_i_ejik:

    play music krosh_i_ejik

    scene черный экран
    with Dissolve(1)

    scene дом ежика
    with Dissolve(1)

    show крош с закрытыми глазами

    krosh "Девяносто восемь, девяносто девять... {w=2} Стоп, а что дальше?"

    show ии 5

    "Неизвестный" "Сто!"

    krosh обычный "А, точно, спасибо!"

    krosh вопрос "Погоди, а что ты такое?"

    "Неизвестный" "Я - искусственный интеллект!"

    krosh обычный "Хм, как-то сложно. {w=2} А у тебя есть имя? Меня, например, зовут Крош,"

    show ежик обычный
    with dissolve

    extend " а это Ёжик."

    hide ии 5

    show ии4

    "Искусственный интелект" "У меня нет имени..."

    krosh обычныйр "Так давай придумаем его!"


    $ iiname = renpy.input("Введите имя", length = 20, default = "Иван Иваныч", allow = " йцукенгшщзхъфывапролджэячсмитьбю-ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ").strip()

    if iiname == "":
        $ iiname = "Иван Иваныч"

    ejik @ вопрос "Хм, а может, [iiname]?"

    hide ии4

    show ии 6

    ii 6 "Ух ты, мне нравится, теперь меня будут звать именно так!"

    krosh вопрос "Значит, ты - искусственный интеллект? {w=2} А что это значит?"

    ii 5 "Это значит, что у меня есть почти такой же мозг, как у вас, и я могу выполнять даже творческие задания, например, писать картины или романы!"
    ii "Также я умею, как и человек, получать информацию и анализировать её. Обычно это помогает людям получать уже готовую информацию и не заморачиваться. Я очень полезен!"

    krosh обычныйр "Вау, очень круто!"

    ejik вопрос "О, это значит, что ты сможешь помочь мне определить, что за животные изображены на фантиках из моей коллекции?"

    menu:

        ejik "{cps=0}О, а ты сможешь помочь мне определить, что за животные изображены на фантиках из моей коллекции?{/cps}"

        "Конечно!":
        
            $ otnkrosh = True
            $ otn += 1
        
            ii "Конечно!"

            play music fantiki

            init python:

                class GameDisplayable(renpy.Displayable):

                    def __init__(self):
                        import pygame

                        renpy.Displayable.__init__(self)

                        self._target_position = [(780, 142.5), (1072.5, 217.5), (952.5, 292.5), (780, 367.5), (1005, 442.5), (645, 517.5), (0, 0)]
                        self._target_position_available = [True, True, True, True, True, True, True, True]

                        self._box_view = BoxView()

                        self._game_result = 0
                        self._FPS = 60
                        self._clock = pygame.time.Clock()
                        self._exit_button = ButtonView(View((1575, 945), Text("Продолжить")), box_view=self._box_view)
                        # self._text_color = "#583613"
                        self._correct_answer = [["белка"], ["слон"], ["медведь", "Медведь", "Медведи", "медведи"], ["петух", "Петух", "Петушок", "петушок"], ["носорог", "Носорог"],
                                                ["собака", "Собака"]]

                        self._list = 0
                        
                        self._conveyor1_image = View((0, 121.5), Image("fon.jpg"), box_view=self._box_view)

                        self._1_image = FlyView(View((142.5, 225), Image("1_photo(1).jpg")), speed=10, box_view=self._box_view)
                        self._2_image = FlyView(View((735, 225), Image("2_photo(1).jpg")), speed=10, box_view=self._box_view)
                        self._3_image = FlyView(View((1327.5, 225), Image("3_photo(1).jpg")), speed=10, box_view=self._box_view)
                        self._4_image = FlyView(View((2062.5, 225), Image("4_photo(1).jpg")), speed=10, box_view=self._box_view)
                        self._5_image = FlyView(View((2655, 225), Image("5_photo(1).jpg")), speed=10, box_view=self._box_view)
                        self._6_image = FlyView(View((3247.5, 225), Image("6_photo(1).jpg")), speed=10, box_view=self._box_view)

                        view_for_input_field_color = "#583613"
                        
                        
                        self._text_input_for_1_image = FlyView(FieldView((156, 597), Solid(view_for_input_field_color, xsize=420, ysize=48),
                                                                         EditText("", (5, 0), max_symbol=21)), speed=10,
                                                               box_view=self._box_view)
                        self._text_input_for_2_image = FlyView(FieldView((748.5, 597), Solid(view_for_input_field_color, xsize=420, ysize=48),
                                                                         EditText("", (5, 0), max_symbol=21)), speed=10,
                                                               box_view=self._box_view)
                        self._text_input_for_3_image = FlyView(FieldView((1341, 597), Solid(view_for_input_field_color, xsize=420, ysize=48),
                                                                         EditText("", (5, 0), max_symbol=21)), speed=10,
                                                               box_view=self._box_view)
                        self._text_input_for_4_image = FlyView(FieldView((2076, 597), Solid(view_for_input_field_color, xsize=420, ysize=48),
                                                                         EditText("", (5, 0), max_symbol=21)), speed=10,
                                                               box_view=self._box_view)
                        self._text_input_for_5_image = FlyView(FieldView((2668.5, 597), Solid(view_for_input_field_color, xsize=420, ysize=48),
                                                                         EditText("", (5, 0), max_symbol=21)), speed=10,
                                                               box_view=self._box_view)
                        self._text_input_for_6_image = FlyView(FieldView((3261, 597), Solid(view_for_input_field_color, xsize=420, ysize=48),
                                                                         EditText("", (5, 0), max_symbol=21)), speed=10,
                                                               box_view=self._box_view)

                        self._text_input = [self._text_input_for_1_image, self._text_input_for_2_image, self._text_input_for_3_image,
                                            self._text_input_for_4_image, self._text_input_for_5_image, self._text_input_for_6_image]
                                            
                        
                        self._conveyor_image = View((0, 121.5), Image("conveyor.png"), box_view=self._box_view)

                        self._box_1_image = FlyView(View((106.5, 193.5), Image("picture_frame.png")), speed=10, box_view=self._box_view)
                        self._box_1_text = FlyView(View((106.5, 547.5), Image("text_frame.png")), speed=10, box_view=self._box_view)

                        self._box_2_image = FlyView(View((699, 193.5), Image("picture_frame.png")), speed=10, box_view=self._box_view)
                        self._box_2_text = FlyView(View((699, 547.5), Image("text_frame.png")), speed=10, box_view=self._box_view)

                        self._box_3_image = FlyView(View((1291.5, 193.5), Image("picture_frame.png")), speed=10, box_view=self._box_view)
                        self._box_3_text = FlyView(View((1291.5, 547.5), Image("text_frame.png")), speed=10, box_view=self._box_view)

                        self._image = Image("tree.png")


                    def render(self, width, height, st, at):
                        r = renpy.Render(width, height)

                        image = renpy.render(self._image, width, height, st, at)
                        r.blit(image, (0, 750))

                        self._box_view.render(r, width, height, st, at)

                        self._clock.tick(self._FPS)
                        renpy.redraw(self, 0)

                        return r

                        # Handles events.


                    def event(self, ev, x, y, st):
                        import pygame

                        exit_game = False
                        if ev.type == pygame.QUIT:
                            self._box_view.exit()

                        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:

                            for value in self._text_input:
                                value.get_view().get_views()[0].event(position=(x, y))

                            if self._exit_button.event((x, y)) and self._list == 0:
                                self._1_image.fly((-525, 225))
                                self._2_image.fly((-525, 225))
                                self._3_image.fly((-525, 225))

                                self._text_input_for_1_image.fly((-525, 596))
                                self._text_input_for_2_image.fly((-525, 596))
                                self._text_input_for_3_image.fly((-525, 596))

                                self._4_image.fly((142.5, 225))
                                self._5_image.fly((735, 225))
                                self._6_image.fly((1327.5, 225))

                                self._text_input_for_4_image.fly((156, 596))
                                self._text_input_for_5_image.fly((748.5, 596))
                                self._text_input_for_6_image.fly((1341, 596))

                                self._list += 1
                            elif self._exit_button.event((x, y)):
                                exit_game = True
                                for i in range(len(self._text_input)):
                                    if self._text_input[i].get_view().get_views()[0].get_text().lower().strip() in self._correct_answer[i]:
                                        self._game_result += 1


                        if self._list == 1:
                            self._exit_button.get_view().get_displayable().set_text("Закончить")

                            renpy.restart_interaction()
                        if ev.type == pygame.KEYDOWN:
                            for value in self._text_input:
                                value.get_view().get_views()[0].event(position=(x, y), symbol=ev.unicode,
                                                                      backspace=ev.key == pygame.K_BACKSPACE)

                        if exit_game:
                            return self._game_result
                        else:
                            raise renpy.IgnoreEvent()


            screen game():

                    default word_game = GameDisplayable()

                    add "дом ежика"

                    add word_game


            label play_game:

                window hide
                $ quick_menu = False

                call screen game

                $ quick_menu = True
                window show

            if _return >= 3:
                ejik "Ух ты! Какой ты умный! Аж [_return] из 6! Спасибо большое!"
                
            else:
                ejik "Ммм... Всего [_return] из 6... Ну спасибо..."

        "Извините, сейчас не могу...":

            ii "Извините, сейчас не могу..."

            ejik обычный "Ну, ладно..."


    krosh обычныйр "Тебя нужно со всеми познакомить! Идем скорее!"

    stop music fadeout 1


label barash_i_nusha:

    play music barash_i_nusha

    scene черный экран
    with Dissolve(1)

    scene качели с
    with fade

    nusha "Ах, Бараш, какие красивые горы и какие вкусные конфеты!"

    barash "Согласен..."

    show крош обычный1

    krosh "Эй, ребят, познакомьтесь, это [iiname], он - искусственный интеллект!"

    scene качели без
    with Dissolve(0.5)

    show крош обычный1

    show ии2

    show ежик обычный1

    show крош обычный1

    show бараш обычный

    show нюша обычная

    nusha "Привет, [iiname], меня зовут Нюша, а это Бараш!"

    barash "Привет. А как ты у нас оказался?"

    ii "Здравстуйте, приятно познакомиться. Начну с самого начала. Меня создали люди, чтобы я им помогал."
    ii "Один известный учёный по имени Алан Тьюринг предположил, что я возможен, после чего, в 1951 году, первый мой прототип, сеть SNARC, создал Марвин Мински."
    ii "А Тьюринг сделал тест, который позволял проверить, насколько я похож на человека."

    barash вопрос "Ух ты, очень интересная история. {w=2} Но, получается, ты же просто робот, имитация жизни. {w=1} Разве может робот написать стихи, создать шедевр?"

    menu:

        barash "{cps=0}Ух ты, очень интересная история. Но, получается, ты же просто робот, имитация жизни. Разве может робот написать стихи, создать шедевр?{/cps}"

        "Я все могу!":

            ii "Я все могу!"
            
            barash обычный "Ах так! Тогда попробуй дописать этот стих!"

        "Могу, но не так хорошо, как ты!":
            $ otnbarash = True
            $ otn += 1

            ii "Могу, но не так хорошо, как ты!"

            barash обычный "О, а помоги мне со стихом!"

    play music stihi

    init python:

        class GameDisplayable1(renpy.Displayable):

            def __init__(self):

                import pygame

                renpy.Displayable.__init__(self)

                self._target_position = [(780, 142.5), (1072.5, 217.5), (952.5, 292.5), (780, 367.5), (1005, 442.5), (645, 517.5), (0, 0)]
                self._target_position_available = [True, True, True, True, True, True, True, True]

                self._box_view = BoxView()

                self._prepare_game_over = False
                self._game_result = 0
                self._FPS = 60
                self._clock = pygame.time.Clock()

                self._correct_answer = ["солнце", "прелестный", "проснись", "сомкнуты", "Авроры", "Звездою"]
                self._text_color = "#000080"

                self._image = View((0, 750), Image("tree.png"), box_view=self._box_view)

                self._text_image = View((270, 0), Image("light_tree.png"), box_view=self._box_view)

                self._exit_button = ButtonView(View((1575, 945), Text("Закончить")))

                self._surf_text = [View((630, 150), Text("Мороз и _____________; день чудесный!", color=self._text_color),
                                        box_view=self._box_view),
                                   View((630, 225), Text("Еще ты дремлешь, друг _____________ —", color=self._text_color),
                                        box_view=self._box_view),
                                   View((630, 300), Text("Пора, красавица, ______________:", color=self._text_color),
                                        box_view=self._box_view),
                                   View((630, 375), Text("Открой _____________ негой взоры", color=self._text_color),
                                        box_view=self._box_view),
                                   View((630, 450), Text("Навстречу северной ______________,", color=self._text_color),
                                        box_view=self._box_view),
                                   View((630, 525), Text("_____________ севера явись!", color=self._text_color),
                                        box_view=self._box_view)]

                self._example_add_text = [
                    FlyView(ButtonView(View((150, 945), Text("солнце"))), speed=5, box_view=self._box_view),
                    FlyView(ButtonView(View((300, 945), Text("сомкнуты"))), speed=5, box_view=self._box_view),
                    FlyView(ButtonView(View((498, 945), Text("Авроры"))), speed=5, box_view=self._box_view),
                    FlyView(ButtonView(View((655.5, 945), Text("прелестный"))), speed=5, box_view=self._box_view),
                    FlyView(ButtonView(View((892.5, 945), Text("Звездою"))), speed=5, box_view=self._box_view),
                    FlyView(ButtonView(View((1068, 945), Text("проснись"))), speed=5, box_view=self._box_view)]
                self.winner = None

            def render(self, width, height, st, at):
                r = renpy.Render(width, height)

                self._box_view.render(r, width, height, st, at)

                if self._prepare_game_over:
                    self._exit_button.render(r, width, height, st, at)

                self._clock.tick(self._FPS)
                renpy.redraw(self, 0)

                return r

            def _put_end_position(self, end_position):
                for i in range(len(self._target_position)):
                    if self._target_position[i] == end_position:
                        self._target_position_available[i] = True
                        return i

            def _get_position_available(self):
                for i in range(len(self._target_position_available)):
                    if self._target_position_available[i]:
                        return i

            # Handles events.
            def event(self, ev, x, y, st):

                import pygame

                exit_game = False
                if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    position_available = self._get_position_available()
                    position = self._target_position[position_available]
                    self._target_position_available[position_available] = False
                    is_used = False
                    for value in self._example_add_text:
                        if value.is_in_start():
                            if value.event((x, y)):
                                value.fly(position)
                                if "".join(value.get_view().get_view().get_displayable().text) == self._correct_answer[
                                    position_available]:
                                    self._game_result += 1
                                is_used = True
                                break
                        elif value.is_in_end():
                            result = value.event((x, y))
                            if result:
                                value.fly(None)
                                if not is_used:
                                    self._put_end_position(position)
                                    is_used = True
                                if self._correct_answer[self._put_end_position(value.get_end_position())] == "".join(
                                        value.get_view().get_view().get_displayable().text):
                                    self._game_result -= 1
                                break
                    if not is_used:
                        self._put_end_position(position)
                    self._prepare_game_over = self._target_position[self._get_position_available()] == (0, 0)
                    if self._prepare_game_over:
                        if self._exit_button.event((x, y)):
                            exit_game = True
                    renpy.restart_interaction()

                if exit_game:
                    return self._game_result
                else:
                    raise renpy.IgnoreEvent()

    screen game1():

        default word_game1 = GameDisplayable1()

        add "качели без"

        add word_game1

    label play_game1:

        window hide
        $ quick_menu = False

        call screen game1

        $ quick_menu = True
        window show


    barash "Ух ты, интересное стихотворение..."

    ejik "Ну ладно, нам нужно познакомить его ещё и со взрослыми, мы пойдём к Карычу!"

    ii "До встречи!"

    hide крош обычный1

    hide ии2

    hide ежик обычный1

    stop music fadeout 1


label dom_karycha:

    play music muskarych

    scene черный экран
    with Dissolve(1)

    scene дом карыча
    with fade

    show ежик обычный1

    show крош обычный1

    show ии3

    krosh "Привет, Кар-Карыч! {w=1} Знакомься, это [iiname], он прилетел к нам от людей!"

    karych "Здравствуй-здравстуй, {w=2} значит, ты - путешественник? Я тоже люблю поездки."

    ii "Здравствуйте, да, я путешествовал по Земле и знаю все места на планете!"
    ii "Также я могу составлять рейтинги самых красивых, чистых, гостеприимных стран, исходя из информации, которую я получаю. Да, её очень много, но я неплохо справляюсь!"

    scene дом без карыча

    show ежик обычный1

    show крош обычный1

    show ии3

    show карыч вопрос

    karych "Слушай, не мог бы ты помочь мне как путешественник путешественнику?"

    menu:

        karych "{cps=0}Слушай, не мог бы ты помочь мне, как путешественник путешественнику?{/cps}"

        "Да, с удовольствием!":

            ii "ДА, с удовольствием!"

            karych "У меня небольшая проблемка: от моих фотографий отклеились названия стран и теперь я не помню, где какие достопримечательности, помоги разобраться."

            play music strany

            init python:
                class GameDisplayable2(renpy.Displayable):

                    def __init__(self):
                        import pygame


                        renpy.Displayable.__init__(self)

                        self._target_position = [(780, 142.5), (1072.5, 217.5), (952.5, 292.5), (780, 367.5), (1005, 442.5), (645, 517.5), (0, 0)]
                        self._target_position_available = [True, True, True, True, True, True, True, True]

                        self._box_view = BoxView()

                        self._game_result = 0
                        self._FPS = 60
                        self._clock = pygame.time.Clock()
                        self._exit_button = ButtonView(View((1575, 945), Text("Продолжить")), box_view=self._box_view)
                        self._correct_answer = [["египет"], ["россия", "ссср"], ["италия"], ["франция"], ["украина", "ссср"],
                                                ["великобритания", "англия"]]

                        self._list = 0
                        
                        self._conveyor1_image = View((0, 121.5), Image("fon.jpg"), box_view=self._box_view)

                        self._1_image = FlyView(View((142.5, 225), Image("1_photo.jpg")), speed=10, box_view=self._box_view)
                        self._2_image = FlyView(View((735, 225), Image("2_photo.jpg")), speed=10, box_view=self._box_view)
                        self._3_image = FlyView(View((1327.5, 225), Image("3_photo.jpg")), speed=10, box_view=self._box_view)
                        self._4_image = FlyView(View((2062.5, 225), Image("4_photo.jpg")), speed=10, box_view=self._box_view)
                        self._5_image = FlyView(View((2655, 225), Image("5_photo.jpg")), speed=10, box_view=self._box_view)
                        self._6_image = FlyView(View((3247.5, 225), Image("6_photo.jpg")), speed=10, box_view=self._box_view)

                        view_for_input_field_color = "#583613"

                        self._text_input_for_1_image = FlyView(FieldView((156, 597), Solid(view_for_input_field_color, xsize=420, ysize=48),
                                                                         EditText("", (5, 0), max_symbol=21)), speed=10,
                                                               box_view=self._box_view)
                        self._text_input_for_2_image = FlyView(FieldView((748.5, 597), Solid(view_for_input_field_color, xsize=420, ysize=48),
                                                                         EditText("", (5, 0), max_symbol=21)), speed=10,
                                                               box_view=self._box_view)
                        self._text_input_for_3_image = FlyView(FieldView((1341, 597), Solid(view_for_input_field_color, xsize=420, ysize=48),
                                                                         EditText("", (5, 0), max_symbol=21)), speed=10,
                                                               box_view=self._box_view)
                        self._text_input_for_4_image = FlyView(FieldView((2076, 597), Solid(view_for_input_field_color, xsize=420, ysize=48),
                                                                         EditText("", (5, 0), max_symbol=21)), speed=10,
                                                               box_view=self._box_view)
                        self._text_input_for_5_image = FlyView(FieldView((2668.5, 597), Solid(view_for_input_field_color, xsize=420, ysize=48),
                                                                         EditText("", (5, 0), max_symbol=21)), speed=10,
                                                               box_view=self._box_view)
                        self._text_input_for_6_image = FlyView(FieldView((3261, 597), Solid(view_for_input_field_color, xsize=420, ysize=48),
                                                                         EditText("", (5, 0), max_symbol=21)), speed=10,
                                                               box_view=self._box_view)

                        self._text_input = [self._text_input_for_1_image, self._text_input_for_2_image, self._text_input_for_3_image,
                                            self._text_input_for_4_image, self._text_input_for_5_image, self._text_input_for_6_image]

                        self._conveyor_image = View((0, 121.5), Image("conveyor.png"), box_view=self._box_view)

                        self._box_1_image = FlyView(View((106.5, 193.5), Image("picture_frame.png")), speed=10, box_view=self._box_view)
                        self._box_1_text = FlyView(View((106.5, 547.5), Image("text_frame.png")), speed=10, box_view=self._box_view)

                        self._box_2_image = FlyView(View((699, 193.5), Image("picture_frame.png")), speed=10, box_view=self._box_view)
                        self._box_2_text = FlyView(View((699, 547.5), Image("text_frame.png")), speed=10, box_view=self._box_view)

                        self._box_3_image = FlyView(View((1291.5, 193.5), Image("picture_frame.png")), speed=10, box_view=self._box_view)
                        self._box_3_text = FlyView(View((1291.5, 547.5), Image("text_frame.png")), speed=10, box_view=self._box_view)

                        self._image = Image("tree.png")


                    def render(self, width, height, st, at):
                        r = renpy.Render(width, height)

                        image = renpy.render(self._image, width, height, st, at)
                        r.blit(image, (0, 750))

                        self._box_view.render(r, width, height, st, at)

                        self._clock.tick(self._FPS)
                        renpy.redraw(self, 0)

                        return r

                        # Handles events.


                    def event(self, ev, x, y, st):
                        import pygame

                        exit_game = False
                        if ev.type == pygame.QUIT:
                            self._box_view.exit()

                        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:

                            for value in self._text_input:
                                value.get_view().get_views()[0].event(position=(x, y))




                            if self._exit_button.event((x, y)) and self._list == 0:
                                self._1_image.fly((-525, 225))
                                self._2_image.fly((-525, 225))
                                self._3_image.fly((-525, 225))

                                self._text_input_for_1_image.fly((-525, 596))
                                self._text_input_for_2_image.fly((-525, 596))
                                self._text_input_for_3_image.fly((-525, 596))

                                self._4_image.fly((142.5, 225))
                                self._5_image.fly((735, 225))
                                self._6_image.fly((1327.5, 225))

                                self._text_input_for_4_image.fly((156, 596))
                                self._text_input_for_5_image.fly((748.5, 596))
                                self._text_input_for_6_image.fly((1341, 596))

                                self._list += 1
                            elif self._exit_button.event((x, y)):
                                exit_game = True
                                for i in range(len(self._text_input)):
                                    if self._text_input[i].get_view().get_views()[0].get_text().lower().strip() in self._correct_answer[
                                        i]:
                                        self._game_result += 1

                        if self._list == 1:
                            self._exit_button.get_view().get_displayable().set_text("Закончить")

                            renpy.restart_interaction()
                        if ev.type == pygame.KEYDOWN:
                            for value in self._text_input:
                                value.get_view().get_views()[0].event(position=(x, y), symbol=ev.unicode,
                                                                      backspace=ev.key == pygame.K_BACKSPACE)

                        if exit_game:
                            return self._game_result
                        else:
                            raise renpy.IgnoreEvent()

            screen game2():

                default word_game2 = GameDisplayable2()

                add "дом без карыча"

                add word_game2


            label play_game2:

                window hide
                $ quick_menu = False

                call screen game2

                $ quick_menu = True
                window show

            if _return >= 3:
                $ otnkarych = True
                $ otn +=1
                karych благодарит "А ты и правда толковый путешественник! Аж [_return] из 6!!!"
            
            else:
                karych благодарит "М-да, давай посмотрим в справочнике... {w} Хм, [_return] из 6..."
        
            stop music fadeout 1

            play music muskarych


        "Нет, сейчас не могу.":

            ii "Нет, сейчас не могу."

            karych плохой "Ну, ладно, как хочешь..."

    karych приглашает "Знаете, а давайте по случаю приезда гостя соберем всех на чаепитие?"

    karych "Крош, Ёжик, позовите сюда всех!"

    "Крош и Ежик" "Сейчас сделаем!"

    hide крош обычный

    hide ежик обычный

label dom_s_sovunyey:

    scene дверь карыча
    with Dissolve(1)

    show совунья обычная

    sovuny "Ох, Карыч, представь себе! С утра еду на лыжах, никого не трогаю, и тут выбегает из кустов НЕЧТО, попадает под лыжи и сразу убегает…"

    show ии 31
    with dissolve

    ii "Вообще-то не НЕЧТО, а искусственный интеллект..."

    sovuny удивленная "А-а?"

    show ии3

    ii "Здрасьте, меня зовут [iiname]. Обычно я могу следить за перемещениями всех машин, помогая людям улучшать дороги, однако распознавать сов на лыжах меня не учили, поэтому вы сбили меня!"

    sovuny обычная "Охх... извините, пожалуйста!"

    menu:

        sovuny "{cps=0}Охх... извините пожалуйста!{/cps}"

        "Простить":
            $ otnsovuny = True
            $ otn += 1

            ii "Ничего страшного, я понимаю, вы испугались, с кем не бывает, забудем этот инцидент"

        "Не прощать":

            hide ии3

            show ии 31

            ii "Ну... Голова всё ещё побаливает..."

label dom_s_losyashem:

    play music naushnay_tema

    scene черный экран
    with Dissolve(1)

    scene дверь карыча
    with dissolve

    show лосяш серьезный1

    show пин обычный1

    losyash "...я вам говорю, эта ракета странная..."

    show карыч представляет
    with dissolve

    karych "Господа, познакомьтесь, это наш гость, [iiname]!"

    show ии3
    with dissolve

    hide карыч представляет
    with dissolve

    losyash восторженный3 "Здравствуйте, друг мой иноземный, добро пожаловать к нам, меня зовут Лосяш."

    pin обычныйр "Йа-йа! А я Пин."

    ii "Приятно с вами познакомиться. Я - искусственный интеллект..."

    losyash боже мой "Боже мой... Это же вы прилетели на ракете, которую я нашёл утром!!!"

    losyash восторженный3 "Я много читал про искусственные интеллекты: вы можете изучать картины и фотографии, говорить, что на них изображено."

    losyash вопрос1 "У меня есть небольшой вопрос: вы же работаете полностью по законам математики?"

    ii "Да, именно. Я подчиняюсь строгим правилам математики и работаю с их помощью. {w=2} Извините, что сбежал с утра, я немного испугался вас."

    losyash "Ох, простите, давайте о более важном: я заметил, что ваш корабль поврежден и его нельзя починить. Если вам вдруг нужно возвращаться, мы с моим товарищем Пином могли бы одолжить вам нашу ракету, что скажете?"

    menu:
        losyash "{cps=0}Ох, простите, давайте о более важном: я заметил, что ваш корабль поврежден и его нельзя починить. Если вам вдруг нужно возвращаться, мы с моим товарищем Пином могли бы одолжить вам нашу ракету, что скажете?{/cps}"

        "Не откажусь от ракеты...":
            $ raketa = True

            ii "Не откажусь от ракеты..."

        "Я, пожалуй, еще задержусь у вас.":

            ii "Я, пожалуй, еще задержусь у вас."

    losyash обычный1 "Хорошо!"

    stop music fadeout 1


label chaepitie:

    play music muskopatych

    scene дом без карыча
    with wipeleft

    show карыч чаепитие


    karych "Ну что ж, вот все и собрались, давайте пить чай!"

    scene дверь карыча
    with vpunch

    show копатыч сонный

    kopatych "Ох, укуси меня пчела, чаепитие, да без меня! Опять я все пропустил!"

    show карыч не злись

    karych "Не злись, Копатыч, у нас гость."

    show ии3
    with dissolve

    pause(2)

    kopatych "Вы меня что, на железку решили променять?"

    hide карыч не злись
    with dissolve

    show лосяш обычный2
    with dissolve

    losyash "Друг мой сонный, это не просто железка, это - искусственный интеллект!"

    ii "Здрасьте, меня зовут [iiname], не беспокойтесь, я не заменю вас, моя задача заключается в том, чтобы помочь вам."

    hide лосяш обычный2
    with dissolve

    kopatych удивленный "А чем ты мне поможешь?"

    ii "О, я многое могу, например, сортировать огурцы по видам, находить сорняки и выдирать их, я буду вам очень полезен!"


    kopatych "О, да ты зверь-машина! Ты точно не опасен???"

    ii "Я совершенно безопасен, уверяю вас."



    kopatych ясненько "Ладно, тогда расскажите подробнее про [iiname]!"

    stop music fadeout 1


label otnosheniy:

    play music sibir

    scene черный экран
    with Dissolve(1)

    scene чаепитие
    with fade

    if otnkrosh:
        krosh "Он очень умный и знает много животных!"

    else:
        krosh "Ну... Он знает немного игр и животных..."

    if otnbarash:
        show бараш довольный
        with Dissolve(0.5)

        barash "А ещё он пишет очень красивые стихи!"

        hide бараш довольный
        with Dissolve(0.5)

    else:
        show бараш серьезный
        with Dissolve(0.5)

        barash "Еще он пишет... стихи..."

        hide бараш серьезный
        with Dissolve(0.5)

    if otnkarych:
        karych "Образованный путешественник!"

    else:
        karych "Он прилетел от людей..."

    if otnsovuny:
        sovuny "С прелестным характером!"

    else:
        sovuny "Своеобразный характер..."
        
    if otn >= 2:
        kopatych "Замечательно! Добро пожаловать к нам, [iiname]!"
    
    else:
        kopatych "Ясненько... Ну, что ж, здравствуй, [iiname]..."

    if raketa:
        jump uletaet

    else:
        jump ne_uletaet

    stop music fadeout 1



label uletaet:

    play music naushnay_tema

    scene черный экран
    with Dissolve(1)

    scene дом без карыча

    show лосяш обычный

    show ии2

    show пин обычный

    losyash "Ну что, Пин, дадим ракету нашему гостю?"

    pin "Йа-йа!"

    play music kosmos

    scene черный экран
    with Dissolve(2)

    scene ракета на земле
    with Dissolve(2)

    "Пин и Лосяш нашли ракету."

    scene ракета в космосе
    with dissolve

    extend "Вскоре [iiname] улетел обратно к людям, оставив Смешариков..."

    play music babochka

    n "Большое спасибо за прохождение \"Интересный Иноземец\"!"

    n "Эта игра была разработана для конкурса \"Большая перемена\" командой \"OLEGOFRIENDER production\" совместно с \"Kasar' & Chursin tehnologies\"."

    n "При создании игры использовались материалы из мультсериала \"Смешарики\" (почти все фоны и спрайты), сериала \"Doctor Who\" (спрайты ИИ) и рисунок А. В. Зарубина (тот что с ракетой)."

    n "Все было сделано благодаря сервису \"КиноПоиск\", функции PrintScrin, программе \"Paint 3D\" и движку \"Ren'Py\""

    n "Эта игра не является коммерческим проектом, так что мы надеемся (очень надеемся), что нас не побьют из-за авторских прав."

    n "Еще раз покорнейше благодарим за потраченное на эту игру личное время!"

    return

label ne_uletaet:

    play music muskarych

    scene чаепитие

    show ии

    ii "Знаете, друзья, я решил остаться и помочь вам развиваться и познавать новое!"

    if otn >= 2:

        show лосяш восторженный2

        losyash "Это замечательно, друг мой благородный!"

        losyash вопрос "Кстати, я недавно создал прибор, который любого может превратить в Смешарика, {w=2} не хотели бы вы опробовать его на себе?"

        menu:

            losyash "{cps=0}Кстати, я недавно создал прибор, который любого может превратить в Смешарика, не хотели бы вы опробовать его на себе?{/cps}"

            "Согласиться":
            
                play music horoshiy_konec
                
                scene черный экран
                with Dissolve(2)
                scene стал смешариком
                with Dissolve(2)
                "В итоге, после испытания прибора на себе, [iiname] стал Смешариком, остальные его приняли и полюбили, они стали жить по соседству и помогать друг другу..."

                play music babochka

                n "Большое спасибо за прохождение \"Интересный Иноземец\"!"

                n "Еще раз покорнейше благодарим за потраченное на эту игру личное время!"

            "Отказаться":
            
                play music neytralnay
            
                scene черный экран
                with Dissolve(2)
                scene упавшая ракета
                with Dissolve(2)
                "[iiname], хоть и не стал полностью Смешариком, остался помогать жителям деревни, однако поселился он в своей собственной ракете, ведь Смешарики все ещё немного сторонились его..."

                play music babochka
                
                n "Большое спасибо за прохождение \"Интересный Иноземец\"!"

                n "Еще раз покорнейше благодарим за потраченное на эту игру личное время!"
                

    else:

        play music neytralnay

        scene упавшая ракета
        "[iiname], хоть и не стал полностью Смешариком, остался помогать жителям деревни, однако поселился он в своей собственной ракете, ведь Смешарики все ещё немного сторонились его..."

        play music babochka
        
        n "Большое спасибо за прохождение \"Интересный Иноземец\"!"


    return




