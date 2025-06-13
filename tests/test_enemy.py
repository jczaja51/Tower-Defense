from game.enemy import Enemy, Troll, Rycerz, Nietoperz

def test_enemy_initialization():
    path = [(0,0), (1,0), (2,0)]
    e = Enemy(path, name="Test", hp=10, speed=1, reward=3)
    assert e.name == "Test"
    assert e.hp == 10
    assert e.position == (0,0)
    assert e.alive

def test_enemy_take_damage_and_die():
    path = [(0,0), (1,0)]
    e = Enemy(path, "Test", 5, 1, 1)
    e.take_damage(3)
    assert e.hp == 2
    assert e.alive
    e.take_damage(2)
    assert e.hp == 0
    assert not e.alive

def test_enemy_move_and_reach_end():
    path = [(0,0), (1,0), (2,0)]
    e = Enemy(path, "Test", 10, 1, 1)
    e.move()
    assert e.position == (1,0)
    e.move()
    assert e.position == (2,0)
    e.move()
    assert not e.alive
    assert e.reached_end

def test_enemy_apply_burn_effect():
    path = [(0,0), (1,0)]
    e = Enemy(path, "Test", 5, 1, 1)
    e.burning = 2
    e.apply_effects()
    assert e.hp == 4
    assert e.burning == 1

def test_troll_regeneration():
    path = [(0,0), (1,0)]
    troll = Troll(path)
    troll.hp = 30
    troll.regen_interval = 2
    troll._regen_counter = 1
    troll.regenerates = True
    troll.apply_effects()
    assert troll.hp == 31  # regeneracja po dwóch turach

def test_rycerz_fire_immune():
    path = [(0,0)]
    knight = Rycerz(path)
    knight.burning = 2
    knight.hp = 10
    knight.apply_effects()
    assert knight.hp == 10
    assert knight.burning == 2

def test_nietoperz_moves_to_target():
    path = [(0,0)]
    bat = Nietoperz(path, start=(0,0), target=(2,2))
    bat.move()
    assert bat.position == (1,1)
    bat.move()
    assert bat.position == (2,2)
    assert not bat.alive
    assert bat.reached_end