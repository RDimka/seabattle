# SeaBattle
import random
import copy
import time

# Класс исключений
class MyError(Exception):
    def __init__(self, text):
        self.txt = text

# класс Dot — класс точек на поле
class Dot():
    x, y = None, None

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

# Класс Ship — корабль на игровом поле, который описывается параметрами:
# Длина.
# Точка, где размещён нос корабля.
# Направление корабля (вертикальное/горизонтальное).
# Количеством жизней (сколько точек корабля ещё не подбито).
# И имеет метод dots, который возвращает список всех точек корабля.
class Ship():
    long, bow_dot, direction, life_num = None, None, None, None
    def __init__(self, *args):
        self.long = args[0]
        self.bow_dot = args[1]
        self.direction = args[2]
        self.life_num = args[3]

    def dots(self):
        ship_dot_list = []
        i = self.long
        x = self.bow_dot.x
        y = self.bow_dot.y
        while i:
            ship_dot_list.append(Dot(x, y))
            if self.direction == "v":
                x += 1
            else:
                y += 1
            i -= 1
        return ship_dot_list  # список всех точек корабля

#класс Board — игровая доска.
class Board():
    def __init__(self, hid=False, alive=7):
        # двумерный списко состояний каждой из клеток, инициализация
        self.board_state = [["O"] * 6 for i in range(6)]

        # Список кораблей доски.
        self.board_ships = [Ship(3, Dot(-1, -1), 'v', 3),
                            Ship(2, Dot(-1, -1), 'v', 2),
                            Ship(2, Dot(-1, -1), 'v', 2),
                            Ship(1, Dot(-1, -1), 'v', 1),
                            Ship(1, Dot(-1, -1), 'v', 1),
                            Ship(1, Dot(-1, -1), 'v', 1),
                            Ship(1, Dot(-1, -1), 'v', 1)]

        # Параметр hid типа bool — информация о том, нужно ли скрывать корабли на доске (для вывода доски врага) или нет (для своей доски).
        self.hid = False

        # Количество живых кораблей на доске.
        self.alive_ships = alive

        # Метод add_ship, который ставит корабль на доску (если ставить не получается, выбрасываем исключения).
    def add_ship(self, ship_num):
        attempt = 2000
        while attempt:
            next_iter = False
            # ориентация корабля случайная
            self.board_ships[ship_num].direction = "v" if random.randint(0, 1) else "h"

            if self.board_ships[ship_num].long > 1:  # для всех, кто больше одной клетки добавляем ограничение на координаты начальной точки
                if self.board_ships[ship_num].direction == "v":
                    self.board_ships[ship_num].bow_dot = Dot(random.randint(0, 6 - self.board_ships[ship_num].long),
                                                             random.randint(0, 5))
                else:
                    self.board_ships[ship_num].bow_dot = Dot(random.randint(0, 5),
                                                             random.randint(0, 6 - self.board_ships[ship_num].long))
            else:  # для единичек
                self.board_ships[ship_num].bow_dot = Dot(random.randint(0, 5), random.randint(0, 5))

            # все координаты коробля
            ship_dots = self.board_ships[ship_num].dots()
            #проверка, нет ли вокруг других кораблей
            ship_dots_area = self.contour(self.board_ships[ship_num])
            for i in ship_dots_area:
                if self.board_state[i.x][i.y] == "s":
                    attempt -= 1
                    next_iter = True
                    break

            if not next_iter:  # удачная попытка, фиксируем корабль
                for i in ship_dots:
                    self.board_state[i.x][i.y] = "s"
                return True
        raise MyError("BoardAddShipFailed") #исключение при не возможности установить корабль на доску

    def contour(self, ship):
        ship_area = []
        ship_current_dot = copy.deepcopy(ship.bow_dot)
        i = ship.long + 2
        ship_current_dot.x = ship_current_dot.x - 1
        ship_current_dot.y = ship_current_dot.y - 1
        if ship.direction == 'v':
            while i:
                if 0 <= ship_current_dot.x <= 5:
                    y = 3
                    while y:  # добавляем точки одной строки
                        if 0 <= ship_current_dot.y <= 5:
                            ship_area.append(Dot(ship_current_dot.x, ship_current_dot.y))
                        ship_current_dot.y += 1
                        y -= 1
                    ship_current_dot.y -= 3
                ship_current_dot.x += 1
                i -= 1

        else:  # горизонтальный
            while i:
                if 0 <= ship_current_dot.y <= 5:
                    y = 3
                    while y:  # добавляем дотчки одного столбца
                        if 0 <= ship_current_dot.x <= 5:
                            ship_area.append(Dot(ship_current_dot.x, ship_current_dot.y))
                        ship_current_dot.x += 1
                        y -= 1
                    ship_current_dot.x -= 3
                ship_current_dot.y += 1
                i -= 1
        return ship_area

    # Метод, который выводит доску в консоль в зависимости от параметра hid.
    def board_layout(self):
        #print()
        print("    | 1 | 2 | 3 | 4 | 5 | 6  ")
        print("  -------------------------- ")

        board = copy.deepcopy(self.board_state)#копируем, что скрыть при необходимости корабли
        if (self.hid==True):
            for i in range(6):
                for j in range(6):
                    board[i][j] = 'O' if  board[i][j] == "s" else board[i][j]

        for i, row in enumerate(board):
            row_str = f"  {i + 1} | {' | '.join(row)} | "
            print(row_str)

    def out(self, dot):
        # проверка в поле?
        return True if dot.x > 5 or dot.y > 5 else False

    # Метод shot, который делает выстрел по доске (если есть попытка выстрелить за пределы и в использованную точку, нужно выбрасывать исключения).
    # выстрел
    def shot(self, dot):
        # try:
        if self.out(dot):
            raise MyError("BoardOutException")
        if self.board_state[dot.x][dot.y] == 'X' or self.board_state[dot.x][dot.y] == 'T':
            raise MyError("UsedPointException")

        # помечаем Т (промах), Х (попал)
        self.board_state[dot.x][dot.y] = "T" if self.board_state[dot.x][dot.y] == "O" else "X"
        # Если попал вернем True и удалим жизнь
        if self.board_state[dot.x][dot.y] == "X":
            for i in self.board_ships:
                if dot in i.dots():
                    i.life_num -= 1
                    if i.life_num == 0:
                        self.alive_ships -= 1
            return True
        else:
            return False


# класс Player — класс игрока в игру (и AI, и пользователь).
class Player():
    def __init__(self, board_player, board_enemy):
        self.board_player = board_player
        self.board_enemy = board_enemy

    # ask — метод, который «спрашивает» игрока, в какую клетку он делает выстрел.
    def ask(self):
        pass

    # move — метод, который делает ход в игре.
    def move(self):
        i = 1000
        while i:
            dot_shot = self.ask()
            try:
                return self.board_enemy.shot(dot_shot)
            except MyError as err:
                print(err)
                i -= 1
        print("Использовал 1000 ходов, следующий )")
        return False

# унаследовать классы AI и User от Player и переопределить в них метод ask. Для AI это будет выбор случайной точки, а для User этот метод будет спрашивать координаты точки из консоли.
class AI(Player):
    def ask(self):
        # случайные координаты точки
        dot = Dot(random.randint(0, 5), random.randint(0, 5))
        print(f"Противник сходил: {dot.x+1} {dot.y+1}")
        return dot

class User(Player):
    def ask(self):
        # Запросить точки
        shot_point = Dot()
        print(" формат ввода координат выстрела: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

        while True:
            cords = input("         Ваш ход: ").split()
            if len(cords) != 2:
                print(" Введите 2 координаты! ")
                continue

            if not (cords[0].isdigit()) or not (cords[1].isdigit()):
                print(" Введите числа от 1 до 6! ")
                continue

            if int(cords[0]) < 1 or int(cords[1]) > 6\
                    or int(cords[1]) < 1 or int(cords[1]) >6:
                print(" Введите числа от 1 до 6! ")
                continue

            shot_point.x, shot_point.y = int(cords[0])-1, int(cords[1])-1
            return shot_point

class Game():
    def __init__(self, user, ai):
        self.user = user
        self.user_board = user.board_player
        self.ai = ai
        self.ai_board = ai.board_player

        # random_board — метод генерирует случайную доску.
    def random_board(self, board):

        create_attempt_num = 10 #количество попыток создать доску
        while create_attempt_num:
            board.__init__()
            # расставляем корабли
            i = 0
            while i < len(board.board_ships):
                try:
                    board.add_ship(i)
                except MyError as er:
                    print(er)
                    create_attempt_num -= 1
                    break
                else:
                    i += 1
            if i == len(board.board_ships):
                create_attempt_num = 0
        return True

        # greet — метод, который в консоли приветствует пользователя и рассказывает о формате ввода.
    def greet(self):
        print("-------------------")
        print("  Приветсвуем вас  ")
        print("      в игре       ")
        print("    морской бой    ")
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")
        pass

        # loop — метод с самим игровым циклом.
    def loop(self):
        while True:
            print("")
            print("Ход игрока:")
            print("")
            print("     Доска противника:")
            self.ai_board.board_layout()

            # self.ai_board.hid = False
            # self.ai_board.board_layout()
            # self.ai_board.hid = True

            while self.user.move():  # True если попал
                print("Попал! Еще один ход.")
                print("")
                print("     Доска противника:")
                self.ai_board.board_layout()

                # self.ai_board.hid = False
                # self.ai_board.board_layout()
                # self.ai_board.hid = True

                if self.ai_board.alive_ships == 0:
                    print("")
                    print("Вы выиграли! Поздравляю!")
                    return True
            print("Промазал!")
            print(" ")

            print("Ход противника:")
            while self.ai.move():  # True если попал
                print("Попал! Еще один ход противника.")
                print(" ")
                print("     Доска игрока:")
                self.user_board.board_layout()
                if self.user_board.alive_ships == 0:
                    print("Вы проиграли!")
                    return True
            print("Промазал!")
            print(" ")
            print("     Доска игрока:")
            self.user_board.board_layout()
            time.sleep(3)
            print(" ")


        # start — запуск игры. Сначала вызываем greet, а потом loop.
    def start(self):
        self.greet()

        self.random_board(self.user_board)
        self.user_board.hid = False
        print(" ")
        print("Доска пользователя")
        self.user_board.board_layout()

        self.random_board(self.ai_board)
        self.ai_board.hid = True
        print(" ")
        print("Доска соперника")
        self.ai_board.board_layout()

        # self.ai_board.hid = True
        # self.ai_board.board_layout()
        # self.ai_board.hid = False
        # self.ai_board.board_layout()
        # self.ai_board.hid = True

        self.loop()
        pass

#Проверки, удалить
board_user = Board()
board_ai = Board()
game = Game(User(board_user, board_ai), AI(board_ai, board_user))
game.start()