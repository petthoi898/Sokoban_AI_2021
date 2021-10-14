
```
$ python sokoban.py --help
```
```
Usage: sokoban.py [options]

Options:
  -h, --help            show this help message and exit
  -l SOKOBANLEVELS, --level=SOKOBANLEVELS
                        level of game to play (test1-10.txt, level1-5.txt)
  -m AGENTMETHOD, --method=AGENTMETHOD
                        research method (bfs, dfs, ucs, astar)
```

`-l`：test1-10.txt, level1-5.txt
`-m`：dfs or greedy
example 1:
python sokoban.py -l test1.txt -m dfs
runtime: 0.09 second
rrUrdllluRRlldrrrUlllururrDLrullldRldrrUruLrdllldrrdrUlllurrurDluLrrdllldrrdrUU
example 2:
python sokoban.py -l test2.txt -m dfs
runtime: 0.00 second
rrrUlldlUrrrUlldrrdllluU
example 3:
python sokoban.py -l test3.txt -m dfs
runtime: 0.34 second
rrdldrdllDRlldlUrrrdrruLrdllLrrrululldRllldRlurrrdrruLrdllUrrdllLrrrullllldRRRlllurrrrrdLrulllllUdrrrrrdlLrrullllldrRRlllurrrrrdLrullluRldrrrdlLrrullllldrRRlllurrrrrdLrulllururulluLrrrdlddldrrrdlLrrullllldrRRlllurrrrrdLrulUlldrrrdlLrrullllldrRRlllurrrrrdLrulllurrUldrdrdlLrrullllldrRRlllurrrrrdLrulllurrululurrDDldldrrrdlLrrulllururDlldrdrruLrdllLrrrululldRllldRlurrrdLrrruLrdlllulldRRRlllurrurrdrdLrulL
example 4:
python sokoban.py -l test4.txt -m dfs
rrrdllllLrrrrrdllllllluRRRR
runtime of dfs: 0.00 second.
example 5:
than 3 minute
example 6:
python sokoban.py -l test6.txt -m dfs
rrdlllluRRlldrrrruLrdllUUUddrrdlllluuuurRlldddrrrruuuLL
runtime of dfs: 0.01 second.
example 7:
python sokoban.py -l test7.txt -m dfs
rdllllurRlldrrrruulLrrdLrdllllurRlldrrrruullLrrrdLrdllllurRlldrrrruulluulldDrrrrdLrdllllUrdrrrulLrrdlllluUrrrrdllLrrrullllUdrrrrdllldlUrrrrulluululldRRllurrrrrdddllldrrrdlllluUrrrruuullllldrDDrrrrdllldlUrrrrulluUlllurrRllldrrrddrrdllllUrrrruuuLrdddllllUdrruuluRllldRRllurrrDllddrrrruuuLrdddlllluurrDDrrdlLrrdlllluRRlldrrrruulllluuruRllldrrrddrrdLrdllllurRlldrrrruuuuuLrdddlllldrrdrUrdllllurrulluuruRllldrrrddlldrrrruLrdllllurRlldrrrruuuuLrdddLrdlllluuuruRllldrrrdDrruuuLrdddlllluuruRllldrrrddrrdlLrrdlllluurrrruuuLrdddllllddrrrrullLrrrdllllUrrrrulluulldDrrrruuulLrrdddlllluulurRRllldrrrddrrdllldlUrrrruuuuLrdddllldrrrdlllluUrrrruuulLrrdddlluulllurRRllldrrrddrrdlllluUdrrrruuuLrdddlllluUruRldrddrrdlllluuuluR
runtime of dfs: 0.82 second.

example 8:
python sokoban.py -l test8.txt -m dfs
llDlurrrdLrullldRDDDDDlllddrrdrruuLrddllulluurrruuuuulurrrdLrullldRdddddlllddrrUruLruuuuulurrrdLrullDDDDDDlddlluuRRllddrrdrruuLrddllulluurrDrUldrrddllUlluurrrUdlllddrrUruLruUddldrrddllulluuRlddrrdrruuluLruuUdddldrrddllulluuRlddrrdrruuluLruuuUddddldrrddllulluuRlddrrdrruuluLruuuuUluRldrdddddldrrddllulluuRRllddrrdrruulUUUUUU
runtime of dfs: 0.11 second.
example 9:
python sokoban.py -l test9.txt -m dfs
dlllUluRRlldrdrrruuLLrrddllUlluurDRlldRdrrruuLLrrddllluluurDrrrddlUrdlllUR
runtime of dfs: 0.40 second.
example 10:
python sokoban.py -l test10.txt -m dfs
dlUrrrdLrulllddrUluRuulDrddrruLrdllUU
runtime of dfs: 0.02 second.