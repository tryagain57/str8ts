# Class str8ts:
# Methoden zum Malen des Grids und der Kästchen, optional mit Möglichkeiten 1-9, aufgerufen von:
    # PrintStr8ts Methode auf PNG File
# Einlesen eines Layouts
# Methoden zur Lösung: Algorithmen
# V4 hat strasseMitSolved nicht mehr: in strasseMinMax enthalten
# V6: guess2 Algorithmus: wenn sonst nicht lösbar, suche 1. Zelle mit 2 Possibilities (Tupel),
    # nimm eine davon als Vermutung
    # und schaue ob lösbar und fehlerfrei.
    # Wenn mit Fehler, dann Vermutung falsch, also andere Possibility richtig.
    # Wenn nicht lösbar, versuche mit 2. Possibility oder anderen Tupel
# V8: guess3 Algorithmus, wenn auch guess2 keine Lösung bringt 

from PIL import Image, ImageDraw, ImageFont
import re, copy, inspect, os

class str8ts:

    label = ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J')

    def __init__(self):
        self.f = [[0] * 9 for i in range(9)]    # instance variable für str8ts Feld:
                                                # 9*9 Matrix als List von Lists mit Dictionary Element
                                                # 1. Index entspricht A..Z, 2. Index 1..9
        for i in range(9):
            for j in range(9):
                self.f[i][j] = {'poss': [1,2,3,4,5,6,7,8,9], 'schwarz': False, 'solved': False}

        self.s = [[0, 0] for i in range(10)]    # setti results:
                                                # s[0] wird nicht verwendet, damit 1-9 den Possibilities entsprechen
                                                # s[i][0] ist horizontal, s[i][1] ist vertikal

        self.printLevel = 'nie'    # in wie weit Algorithmus-Lösungen gedruckt werden: nie, gering, viel, alles
        self.fileStamm = 'str8ts_'
        self.it = 0  # Iteration count für Lösung
        self.anzSolved = 0
        self.anzPrintA = 0

    def algZahlFix(self):
        # Algorithmus: löscht für alle solved Zellen die entsprechenden Possibilities in den übrigen Zellen
        for i in range(9):
            for j in range(9):
                if self.f[i][j]['solved']:
                    z = self.f[i][j]['poss'][0]
                    for k in range(9):
                        if not self.f[i][k]['solved']:
                            if self.f[i][k]['poss'].count(z) > 0:
                                self.printA('algZahlFix removes '+str(z)+' von Zelle '+self.label[i]+str(k+1))
                                self.f[i][k]['poss'].remove(z)
                                if len(self.f[i][k]['poss']) == 1:
                                    self.f[i][k]['solved'] = True
        for j in range(9):
            for i in range(9):
                if self.f[i][j]['solved']:
                    z = self.f[i][j]['poss'][0]
                    for k in range(9):
                        if not self.f[k][j]['solved']:
                            if self.f[k][j]['poss'].count(z) > 0:
                                self.printA('algZahlFix removes '+str(z)+' von Zelle '+self.label[k]+str(j+1))
                                self.f[k][j]['poss'].remove(z)
                                if len(self.f[k][j]['poss']) == 1:
                                    self.f[k][j]['solved'] = True

    def strasseMinMax(self):
        # Strasse ist Sequenz zwischen zwei Schwarzen / Rand.
        # min, max sind die minimalen, maximalen Possibilities
        # StrasseMinMax schaut, ob min möglich ist,
        #   denn dann müssen alle Zellen eine Possibility von min bis min + len(Strasse) - 1 enthalten
        #   und außerhalb der Strasse darf keine Zelle nur Possibilities von min bis len(Strasse) - 1 haben
        # Wenn nicht, kann min eleminiert werden
        # entsprechend für max ...
        for i in range(9):
            end = -1
            while end < 9:
                start = end + 1
                end = start
                while end < 9 and not self.f[i][end]['schwarz']:
                    end += 1
                # Strasse: von start bis end-1
                if end < start+2:   # Strasse mit Länge 0 oder 1
                    continue
                min = 10
                for j in range(start, end):
                    if self.f[i][j]['poss'][0] < min:
                        min = self.f[i][j]['poss'][0]
                max = 0
                for j in range(start, end):
                    if self.f[i][j]['poss'][-1] > max:
                        max = self.f[i][j]['poss'][-1]
                l = end - start # Länge der Strasse
                minOk = True
                maxOk = True
                for j in range(9):
                    if j < start or j >= end:
                        # ausserhalb Strasse
                        if set(self.f[i][j]['poss']) <= set(range(min, min + l)):
                            minOk = False
                            break
                        if set(self.f[i][j]['poss']) <= set(range(max - l + 1, max + 1)):
                            maxOk = False
                            break
                    elif self.f[i][j]['poss'][0] > min + l - 1:
                        minOk = False
                        break
                    elif self.f[i][j]['poss'][-1] < max - l + 1:
                        maxOk = False
                        break
                if not minOk:
                    for j in range(start, end):
                        if min in self.f[i][j]['poss']:
                            self.f[i][j]['poss'].remove(min)
                            self.printA('strasseMinMax removes '+str(min)+' von Zelle '+self.label[i]+str(j+1))
                            if len(self.f[i][j]['poss']) == 1:
                                self.f[i][j]['solved'] = True
                if not maxOk:
                    for j in range(start, end):
                        if max in self.f[i][j]['poss']:
                            self.f[i][j]['poss'].remove(max)
                            self.printA('strasseMinMax removes '+str(max)+' von Zelle '+self.label[i]+str(j+1))
                            if len(self.f[i][j]['poss']) == 1:
                                self.f[i][j]['solved'] = True
        for j in range(9):
            end = -1
            while end < 9:
                start = end + 1
                end = start
                while end < 9 and not self.f[end][j]['schwarz']:
                    end += 1
                # Strasse: von start bis end-1
                if end < start+2:   # Strasse mit Länge 0 oder 1
                    continue
                min = 10
                for i in range(start, end):
                    if self.f[i][j]['poss'][0] < min:
                        min = self.f[i][j]['poss'][0]
                max = 0
                for i in range(start, end):
                    if self.f[i][j]['poss'][-1] > max:
                        max = self.f[i][j]['poss'][-1]
                l = end - start # Länge der Strasse
                minOk = True
                maxOk = True
                for i in range(9):
                    if i < start or i >= end:
                        # ausserhalb Strasse
                        if set(self.f[i][j]['poss']) <= set(range(min, min + l)):
                            minOk = False
                            break
                        if set(self.f[i][j]['poss']) <= set(range(max - l + 1, max + 1)):
                            maxOk = False
                            break
                    elif self.f[i][j]['poss'][0] > min + l - 1:
                        minOk = False
                        break
                    elif self.f[i][j]['poss'][-1] < max - l + 1:
                        maxOk = False
                        break
                if not minOk:
                    for i in range(start, end):
                        if min in self.f[i][j]['poss']:
                            self.f[i][j]['poss'].remove(min)
                            self.printA('strasseMinMax removes '+str(min)+' von Zelle '+self.label[i]+str(j+1))
                            if len(self.f[i][j]['poss']) == 1:
                                self.f[i][j]['solved'] = True
                if not maxOk:
                    for i in range(start, end):
                        if max in self.f[i][j]['poss']:
                            self.f[i][j]['poss'].remove(max)
                            self.printA('strasseMinMax removes '+str(max)+' von Zelle '+self.label[i]+str(j+1))
                            if len(self.f[i][j]['poss']) == 1:
                                self.f[i][j]['solved'] = True

    def strandedSeq(self):
        # Bestimme Sequenzen all der Possibles in einer Strasse.
        # Hier Sequenz ist Aneinanderreihung von Zahlen ohne Gap.
        # strandedSeq ist eine solche Sequenz, deren Länge kleiner len(Strasse) ist und damit eleminiert werden kann
        for i in range(9):
            end = -1
            while end < 9:
                start = end + 1
                end = start
                while end < 9 and not self.f[i][end]['schwarz']:
                    end += 1
                # Strasse: von start bis end-1
                if end < start+2:   # Strasse mit Länge 0 oder 1
                    continue
                min = 10
                for j in range(start, end):
                    if self.f[i][j]['poss'][0] < min:
                        min = self.f[i][j]['poss'][0]
                max = 0
                for j in range(start, end):
                    if self.f[i][j]['poss'][-1] > max:
                        max = self.f[i][j]['poss'][-1]
                # Bestimme Sequenzen von min bis max
                minSeq = min
                for m in range(min+1, max):
                    isGap = True
                    for j in range(start, end):
                        if m in self.f[i][j]['poss']:
                            isGap = False
                            break
                    if isGap:
                        if m > minSeq:  # keine 2 Gaps hintereinander
                            if m-minSeq < end-start:
                                self.printA('strandedSeq removes '+str(minSeq)+' bis '+str(m-1)+' von Zellen '+self.label[i]+str(start+1)+'..'+str(end))
                                for j in range(start, end):
                                    for p in range(minSeq, m):
                                        if p in self.f[i][j]['poss']:           # möglich, dass nicht gesamte zu
                                            self.f[i][j]['poss'].remove(p)      # eleminierende Sequenz in jeder
                                            if len(self.f[i][j]['poss']) == 1:  # Zelle der Strasse auftritt
                                                self.f[i][j]['solved'] = True
                        minSeq = m+1
                if max - minSeq + 1 < end - start:
                    self.printA('strandedSeq removes '+str(minSeq)+' bis '+str(max)+' von Zellen '+self.label[i]+str(start+1)+'..'+str(end))
                    for j in range(start, end):
                        for p in range(minSeq, max+1):
                            if p in self.f[i][j]['poss']:
                                self.f[i][j]['poss'].remove(p)
                                if len(self.f[i][j]['poss']) == 1:
                                    self.f[i][j]['solved'] = True

        for j in range(9):
            end = -1
            while end < 9:
                start = end + 1
                end = start
                while end < 9 and not self.f[end][j]['schwarz']:
                    end += 1
                # Strasse: von start bis end-1
                if end < start+2:   # Strasse mit Länge 0 oder 1
                    continue
                min = 10
                for i in range(start, end):
                    if self.f[i][j]['poss'][0] < min:
                        min = self.f[i][j]['poss'][0]
                max = 0
                for i in range(start, end):
                    if self.f[i][j]['poss'][-1] > max:
                        max = self.f[i][j]['poss'][-1]
                # Bestimme Sequenzen von min bis max
                minSeq = min
                for m in range(min+1, max):
                    isGap = True
                    for i in range(start, end):
                        if m in self.f[i][j]['poss']:
                            isGap = False
                            break
                    if isGap:
                        if m > minSeq:  # keine 2 Gaps hintereinander
                            if m-minSeq < end-start:
                                self.printA('strandedSeq removes '+str(minSeq)+' bis '+str(m-1)+' von Zellen '+self.label[start]+'..'+self.label[end-1]+str(j+1))
                                for i in range(start, end):
                                    for p in range(minSeq, m):
                                        if p in self.f[i][j]['poss']:
                                            self.f[i][j]['poss'].remove(p)
                                            if len(self.f[i][j]['poss']) == 1:
                                                self.f[i][j]['solved'] = True
                        minSeq = m+1
                if max - minSeq + 1 < end - start:
                    self.printA('strandedSeq removes '+str(minSeq)+' bis '+str(max)+' von Zellen '+self.label[start]+'..'+self.label[end-1]+str(j+1))
                    for i in range(start, end):
                        for p in range(minSeq, max+1):
                            if p in self.f[i][j]['poss']:
                                self.f[i][j]['poss'].remove(p)
                                if len(self.f[i][j]['poss']) == 1:
                                    self.f[i][j]['solved'] = True

    def requiredDigits(self):
        # Bestimme required Digits all der Possibles in einer Strasse.
        # Bei Possibles von min ... max und l=len(Strasse) sind die required Digits max-l+1 ... min+l-1
        # Die required Digits können außerhalb der Strasse eleminiert werden
        # Hat innerhalb der Strasse nur eine Zelle ein required Digit, dann ist dies die Lösung der Zelle
        for i in range(9):
            end = -1
            while end < 9:
                start = end + 1
                end = start
                while end < 9 and not self.f[i][end]['schwarz']:
                    end += 1
                # Strasse: von start bis end-1
                if end < start+2:   # Strasse mit Länge 0 oder 1
                    continue
                min = 10
                for j in range(start, end):
                    if self.f[i][j]['poss'][0] < min:
                        min = self.f[i][j]['poss'][0]
                max = 0
                for j in range(start, end):
                    if self.f[i][j]['poss'][-1] > max:
                        max = self.f[i][j]['poss'][-1]
                # Iteriere über die required Digits p
                for p in range(max-(end-start)+1, min+end-start):
                    for j in range(start):
                        if p in self.f[i][j]['poss']:
                            self.f[i][j]['poss'].remove(p)
                            self.printA('requiredDigits removes '+str(p)+' von Zelle '+self.label[i]+str(j+1))
                            if len(self.f[i][j]['poss']) == 1:
                                self.f[i][j]['solved'] = True
                    for j in range(end, 9):
                        if p in self.f[i][j]['poss']:
                            self.f[i][j]['poss'].remove(p)
                            self.printA('requiredDigits removes '+str(p)+' von Zelle '+self.label[i]+str(j+1))
                            if len(self.f[i][j]['poss']) == 1:
                                self.f[i][j]['solved'] = True
                    unique = 0
                    for j in range(start, end):
                        if p in self.f[i][j]['poss']:
                            unique += 1
                            found = j
                    if unique == 1:
                        if not self.f[i][found]['solved']:
                            self.printA('requiredDigits solves Zelle ' + self.label[i] + str(found + 1) + ' mit ' + str(p))
                            self.f[i][found]['poss'] = [p]
                            self.f[i][found]['solved'] = True

        for j in range(9):
            end = -1
            while end < 9:
                start = end + 1
                end = start
                while end < 9 and not self.f[end][j]['schwarz']:
                    end += 1
                # Strasse: von start bis end-1
                if end < start+2:   # Strasse mit Länge 0 oder 1
                    continue
                min = 10
                for i in range(start, end):
                    if self.f[i][j]['poss'][0] < min:
                        min = self.f[i][j]['poss'][0]
                max = 0
                for i in range(start, end):
                    if self.f[i][j]['poss'][-1] > max:
                        max = self.f[i][j]['poss'][-1]
                # Iteriere über die required Digits p
                for p in range(max-(end-start)+1, min+end-start):
                    for i in range(start):
                        if p in self.f[i][j]['poss']:
                            self.f[i][j]['poss'].remove(p)
                            self.printA('requiredDigits removes '+str(p)+' von Zelle '+self.label[i]+str(j+1))
                            if len(self.f[i][j]['poss']) == 1:
                                self.f[i][j]['solved'] = True
                    for i in range(end, 9):
                        if p in self.f[i][j]['poss']:
                            self.f[i][j]['poss'].remove(p)
                            self.printA('requiredDigits removes '+str(p)+' von Zelle '+self.label[i]+str(j+1))
                            if len(self.f[i][j]['poss']) == 1:
                                self.f[i][j]['solved'] = True
                    unique = 0
                    for i in range(start, end):
                        if p in self.f[i][j]['poss']:
                            unique += 1
                            found = i
                    if unique == 1:
                        if not self.f[found][j]['solved']:
                            self.printA('requiredDigits solves Zelle ' + self.label[found] + str(j + 1) + ' mit ' + str(p))
                            self.f[found][j]['poss'] = [p]
                            self.f[found][j]['solved'] = True

    def strasse23(self):
        # Strasse ist Sequenz zwischen zwei Schwarzen / Rand.
        # Strasse2 optimiert Strassen der Länge 2:
        #   für jede Possibility p muss die benachbarte Possibility p-1 oder p+1 sein
        # Entsprechend für Strassen der Länge 3: von p maximal bis p-2 / p+2
        for i in range(9):
            end = -1
            while end < 9:
                start = end + 1
                end = start
                while end < 9 and not self.f[i][end]['schwarz']:
                    end += 1
                # Strasse: von start bis end-1
                if end < start+2:   # Strasse mit Länge 0 oder 1
                    continue
                elif end - start == 2:
                    for j in (0, 1):
                        k1 = start + j
                        k2 = end - j - 1
                        if not self.f[i][k1]['solved']:
                            possCopy = copy.copy(self.f[i][k1]['poss'])
                            for p in possCopy:
                                if not p-1 in self.f[i][k2]['poss'] and not p+1 in self.f[i][k2]['poss']:
                                    self.f[i][k1]['poss'].remove(p)
                                    self.printA('strasse23 removes ' + str(p) + ' von Zelle ' + self.label[i] + str(k1+1))
                                    if len(self.f[i][k1]['poss']) == 1:
                                        self.f[i][k1]['solved'] = True
                elif end - start == 3:
                    for j in (0, 1, 2):
                        k1 = start + j
                        k2 = start + (j + 1)%3
                        k3 = start + (j + 2)%3
                        if not self.f[i][k1]['solved']:
                            possCopy = copy.copy(self.f[i][k1]['poss'])
                            for p in possCopy:
                                weg = True
                                if p-1 in self.f[i][k2]['poss']:
                                    if p-2 in self.f[i][k3]['poss'] or p+1 in self.f[i][k3]['poss']:
                                        weg = False
                                if p-2 in self.f[i][k2]['poss'] and p-1 in self.f[i][k3]['poss']:
                                    weg = False
                                if p+1 in self.f[i][k2]['poss']:
                                    if p+2 in self.f[i][k3]['poss'] or p-1 in self.f[i][k3]['poss']:
                                        weg = False
                                if p+2 in self.f[i][k2]['poss'] and p+1 in self.f[i][k3]['poss']:
                                    weg = False
                                if weg:
                                    self.f[i][k1]['poss'].remove(p)
                                    self.printA('strasse23 removes ' + str(p) + ' von Zelle ' + self.label[i] + str(k1+1))
                                    if len(self.f[i][k1]['poss']) == 1:
                                        self.f[i][k1]['solved'] = True

        for j in range(9):
            end = -1
            while end < 9:
                start = end + 1
                end = start
                while end < 9 and not self.f[end][j]['schwarz']:
                    end += 1
                # Strasse: von start bis end-1
                if end < start+2:   # Strasse mit Länge 0 oder 1
                    continue
                elif end - start == 2:
                    for i in (0, 1):
                        k1 = start + i
                        k2 = end - i - 1
                        if not self.f[k1][j]['solved']:
                            possCopy = copy.copy(self.f[k1][j]['poss'])
                            for p in possCopy:
                                if not p-1 in self.f[k2][j]['poss'] and not p+1 in self.f[k2][j]['poss']:
                                    self.f[k1][j]['poss'].remove(p)
                                    self.printA('strasse23 removes ' + str(p) + ' von Zelle ' + self.label[k1] + str(j+1))
                                    if len(self.f[k1][j]['poss']) == 1:
                                        self.f[k1][j]['solved'] = True
                elif end - start == 3:
                    for i in (0, 1, 2):
                        k1 = start + i
                        k2 = start + (i + 1)%3
                        k3 = start + (i + 2)%3
                        if not self.f[k1][j]['solved']:
                            possCopy = copy.copy(self.f[k1][j]['poss'])
                            for p in possCopy:
                                weg = True
                                if p-1 in self.f[k2][j]['poss']:
                                    if p-2 in self.f[k3][j]['poss'] or p+1 in self.f[k3][j]['poss']:
                                        weg = False
                                if p-2 in self.f[k2][j]['poss'] and p-1 in self.f[k3][j]['poss']:
                                    weg = False
                                if p+1 in self.f[k2][j]['poss']:
                                    if p+2 in self.f[k3][j]['poss'] or p-1 in self.f[k3][j]['poss']:
                                        weg = False
                                if p+2 in self.f[k2][j]['poss'] and p+1 in self.f[k3][j]['poss']:
                                    weg = False
                                if weg:
                                    self.f[k1][j]['poss'].remove(p)
                                    self.printA('strasse23 removes ' + str(p) + ' von Zelle ' + self.label[k1] + str(j+1))
                                    if len(self.f[k1][j]['poss']) == 1:
                                        self.f[k1][j]['solved'] = True

    def naked2(self):
        # naked2 sucht 2 identische Tupel in Reihe/Spalte
        #   dann sind die Possibilities des Tupels im Rest der Reihe/Spalte eleminierbar:
        for i in range(9):
            for j in range(9):
                if len(self.f[i][j]['poss']) != 2:
                    continue
                for k in range(j+1, 9):
                    if len(self.f[i][k]['poss']) == 2 and self.f[i][j]['poss'] == self.f[i][k]['poss']:
                        for p in self.f[i][k]['poss']:
                            for l in range(9):
                                if l != j and l != k:
                                    if p in self.f[i][l]['poss']:
                                        self.f[i][l]['poss'].remove(p)
                                        self.printA('naked2 removes '+str(p)+' von Zelle '+self.label[i]+str(l+1))
                                        if len(self.f[i][l]['poss']) == 1:
                                            self.f[i][l]['solved'] = True
                        break
        for j in range(9):
            for i in range(9):
                if len(self.f[i][j]['poss']) != 2:
                    continue
                for k in range(i+1, 9):
                    if len(self.f[k][j]['poss']) == 2 and self.f[i][j]['poss'] == self.f[k][j]['poss']:
                        for p in self.f[k][j]['poss']:
                            for l in range(9):
                                if l != i and l != k:
                                    if p in self.f[l][j]['poss']:
                                        self.f[l][j]['poss'].remove(p)
                                        self.printA('naked2 removes '+str(p)+' von Zelle '+self.label[l]+str(j+1))
                                        if len(self.f[l][j]['poss']) == 1:
                                            self.f[l][j]['solved'] = True

    def naked3(self):
        # naked3 sucht 3 Tripel in Reihe/Spalte, die max. 3 Possibilities haben
        #   und deren Possibilities aus genau 3 Digits kommen.
        #   Dann sind diese Digits im Rest der Reihe/Spalte eleminierbar:
        for i in range(9):
            for j in range(9):
                if len(self.f[i][j]['poss']) != 2 and len(self.f[i][j]['poss']) != 3:
                    continue
                for k1 in range(j + 1, 9):
                    if len(self.f[i][k1]['poss']) != 2 and len(self.f[i][k1]['poss']) != 3:
                        continue
                    for k2 in range(k1 + 1, 9):
                        if len(self.f[i][k2]['poss']) != 2 and len(self.f[i][k2]['poss']) != 3:
                            continue
                        digits = set(self.f[i][j]['poss']+self.f[i][k1]['poss']+self.f[i][k2]['poss'])
                        if len(digits) == 3:
                            for l in range(9):
                                if l == j or l == k1 or l == k2:
                                    continue
                                for p in digits:
                                    if p in self.f[i][l]['poss']:
                                        self.f[i][l]['poss'].remove(p)
                                        self.printA('naked3 removes '+str(p)+' von Zelle '+self.label[i]+str(l+1))
                                        if len(self.f[i][l]['poss']) == 1:
                                            self.f[i][l]['solved'] = True
                            break
        for j in range(9):
            for i in range(9):
                if len(self.f[i][j]['poss']) != 2 and len(self.f[i][j]['poss']) != 3:
                    continue
                for k1 in range(i + 1, 9):
                    if len(self.f[k1][j]['poss']) != 2 and len(self.f[k1][j]['poss']) != 3:
                        continue
                    for k2 in range(k1 + 1, 9):
                        if len(self.f[k2][j]['poss']) != 2 and len(self.f[k2][j]['poss']) != 3:
                            continue
                        digits = set(self.f[i][j]['poss']+self.f[k1][j]['poss']+self.f[k2][j]['poss'])
                        if len(digits) == 3:
                            for l in range(9):
                                if l == i or l == k1 or l == k2:
                                    continue
                                for p in digits:
                                    if p in self.f[l][j]['poss']:
                                        self.f[l][j]['poss'].remove(p)
                                        self.printA('naked3 removes '+str(p)+' von Zelle '+self.label[l]+str(j+1))
                                        if len(self.f[l][j]['poss']) == 1:
                                            self.f[l][j]['solved'] = True
                            break

    def naked4(self):
        # naked4 sucht 4 Quadrupel in Reihe/Spalte, die max. 4 Possibilities haben
        #   und deren Possibilities aus genau 4 Digits kommen.
        #   Dann sind diese Digits im Rest der Reihe/Spalte eleminierbar:
        for i in range(9):
            for j in range(9):
                if len(self.f[i][j]['poss'])!=2 and len(self.f[i][j]['poss'])!=3 and len(self.f[i][j]['poss'])!=4:
                    continue
                for k1 in range(j + 1, 9):
                    if len(self.f[i][k1]['poss'])!=2 and len(self.f[i][k1]['poss'])!=3 and len(self.f[i][k1]['poss'])!=4:
                        continue
                    for k2 in range(k1 + 1, 9):
                        if len(self.f[i][k2]['poss'])!=2 and len(self.f[i][k2]['poss'])!=3 and len(self.f[i][k2]['poss'])!=4:
                            continue
                        for k3 in range(k2 + 1, 9):
                            if len(self.f[i][k3]['poss'])!=2 and len(self.f[i][k3]['poss'])!=3 and len(self.f[i][k3]['poss'])!=4:
                                continue
                            digits = set(self.f[i][j]['poss']+self.f[i][k1]['poss']+self.f[i][k2]['poss']+self.f[i][k3]['poss'])
                            if len(digits) == 4:
                                for l in range(9):
                                    if l == j or l == k1 or l == k2 or l == k3:
                                        continue
                                    for p in digits:
                                        if p in self.f[i][l]['poss']:
                                            self.f[i][l]['poss'].remove(p)
                                            self.printA('naked4 removes '+str(p)+' von Zelle '+self.label[i]+str(l+1))
                                            if len(self.f[i][l]['poss']) == 1:
                                                self.f[i][l]['solved'] = True
                                break
        for j in range(9):
            for i in range(9):
                if len(self.f[i][j]['poss'])!=2 and len(self.f[i][j]['poss'])!=3 and len(self.f[i][j]['poss'])!=4:
                    continue
                for k1 in range(i + 1, 9):
                    if len(self.f[k1][j]['poss'])!=2 and len(self.f[k1][j]['poss'])!=3 and len(self.f[k1][j]['poss'])!=4:
                        continue
                    for k2 in range(k1 + 1, 9):
                        if len(self.f[k2][j]['poss'])!=2 and len(self.f[k2][j]['poss'])!=3 and len(self.f[k2][j]['poss'])!=4:
                            continue
                        for k3 in range(k2 + 1, 9):
                            if len(self.f[k3][j]['poss'])!=2 and len(self.f[k3][j]['poss'])!=3 and len(self.f[k3][j]['poss'])!=4:
                                continue
                            digits = set(self.f[i][j]['poss']+self.f[k1][j]['poss']+self.f[k2][j]['poss']+self.f[k3][j]['poss'])
                            if len(digits) == 4:
                                for l in range(9):
                                    if l == i or l == k1 or l == k2 or l == k3:
                                        continue
                                    for p in digits:
                                        if p in self.f[l][j]['poss']:
                                            self.f[l][j]['poss'].remove(p)
                                            self.printA('naked4 removes '+str(p)+' von Zelle '+self.label[l]+str(j+1))
                                            if len(self.f[l][j]['poss']) == 1:
                                                self.f[l][j]['solved'] = True
                                break

    def naked5(self):
        # naked5 sucht 5 Quintupel in Reihe/Spalte, die max. 5 Possibilities haben
        #   und deren Possibilities aus genau 5 Digits kommen.
        #   Dann sind diese Digits im Rest der Reihe/Spalte eleminierbar:
        for i in range(9):
            for j in range(9):
                if len(self.f[i][j]['poss']) == 1 or len(self.f[i][j]['poss']) > 5:
                    continue
                for k1 in range(j + 1, 9):
                    if len(self.f[i][k1]['poss']) == 1 or len(self.f[i][k1]['poss']) > 5:
                        continue
                    for k2 in range(k1 + 1, 9):
                        if len(self.f[i][k2]['poss']) == 1 or len(self.f[i][k2]['poss']) > 5:
                            continue
                        for k3 in range(k2 + 1, 9):
                            if len(self.f[i][k3]['poss']) == 1 or len(self.f[i][k3]['poss']) > 5:
                                continue
                            for k4 in range(k3 + 1, 9):
                                if len(self.f[i][k4]['poss']) == 1 or len(self.f[i][k4]['poss']) > 5:
                                    continue
                                digits = set(self.f[i][j]['poss']+self.f[i][k1]['poss']+self.f[i][k2]['poss']+self.f[i][k3]['poss']+self.f[i][k4]['poss'])
                                if len(digits) == 5:
                                    for l in range(9):
                                        if l == j or l == k1 or l == k2 or l == k3 or l == k4:
                                            continue
                                        for p in digits:
                                            if p in self.f[i][l]['poss']:
                                                self.f[i][l]['poss'].remove(p)
                                                self.printA('naked5 removes '+str(p)+' von Zelle '+self.label[i]+str(l+1))
                                                if len(self.f[i][l]['poss']) == 1:
                                                    self.f[i][l]['solved'] = True
                                    break
        for j in range(9):
            for i in range(9):
                if len(self.f[i][j]['poss']) == 1 or len(self.f[i][j]['poss']) > 5:
                    continue
                for k1 in range(i + 1, 9):
                    if len(self.f[k1][j]['poss']) == 1 or len(self.f[k1][j]['poss']) > 5:
                        continue
                    for k2 in range(k1 + 1, 9):
                        if len(self.f[k2][j]['poss']) == 1 or len(self.f[k2][j]['poss']) > 5:
                            continue
                        for k3 in range(k2 + 1, 9):
                            if len(self.f[k3][j]['poss']) == 1 or len(self.f[k3][j]['poss']) > 5:
                                continue
                            for k4 in range(k3 + 1, 9):
                                if len(self.f[k4][j]['poss']) == 1 or len(self.f[k4][j]['poss']) > 5:
                                    continue
                                digits = set(self.f[i][j]['poss']+self.f[k1][j]['poss']+self.f[k2][j]['poss']+self.f[k3][j]['poss']+self.f[k4][j]['poss'])
                                if len(digits) == 5:
                                    for l in range(9):
                                        if l == i or l == k1 or l == k2 or l == k3 or l == k4:
                                            continue
                                        for p in digits:
                                            if p in self.f[l][j]['poss']:
                                                self.f[l][j]['poss'].remove(p)
                                                self.printA('naked5 removes '+str(p)+' von Zelle '+self.label[l]+str(j+1))
                                                if len(self.f[l][j]['poss']) == 1:
                                                    self.f[l][j]['solved'] = True
                                    break

    def naked6(self):
        for i in range(9):
            for j in range(9):
                if len(self.f[i][j]['poss']) == 1 or len(self.f[i][j]['poss']) > 6:
                    continue
                for k1 in range(j + 1, 9):
                    if len(self.f[i][k1]['poss']) == 1 or len(self.f[i][k1]['poss']) > 6:
                        continue
                    for k2 in range(k1 + 1, 9):
                        if len(self.f[i][k2]['poss']) == 1 or len(self.f[i][k2]['poss']) > 6:
                            continue
                        for k3 in range(k2 + 1, 9):
                            if len(self.f[i][k3]['poss']) == 1 or len(self.f[i][k3]['poss']) > 6:
                                continue
                            for k4 in range(k3 + 1, 9):
                                if len(self.f[i][k4]['poss']) == 1 or len(self.f[i][k4]['poss']) > 6:
                                    continue
                                for k5 in range(k4 + 1, 9):
                                    if len(self.f[i][k5]['poss']) == 1 or len(self.f[i][k5]['poss']) > 6:
                                        continue
                                    digits = set(self.f[i][j]['poss']+self.f[i][k1]['poss']+self.f[i][k2]['poss']+self.f[i][k3]['poss']+self.f[i][k4]['poss']+self.f[i][k5]['poss'])
                                    if len(digits) == 6:
                                        for l in range(9):
                                            if l == j or l == k1 or l == k2 or l == k3 or l == k4 or l == k5:
                                                continue
                                            for p in digits:
                                                if p in self.f[i][l]['poss']:
                                                    self.f[i][l]['poss'].remove(p)
                                                    self.printA('naked6 removes '+str(p)+' von Zelle '+self.label[i]+str(l+1))
                                                    if len(self.f[i][l]['poss']) == 1:
                                                        self.f[i][l]['solved'] = True
                                        break
        for j in range(9):
            for i in range(9):
                if len(self.f[i][j]['poss']) == 1 or len(self.f[i][j]['poss']) > 6:
                    continue
                for k1 in range(i + 1, 9):
                    if len(self.f[k1][j]['poss']) == 1 or len(self.f[k1][j]['poss']) > 6:
                        continue
                    for k2 in range(k1 + 1, 9):
                        if len(self.f[k2][j]['poss']) == 1 or len(self.f[k2][j]['poss']) > 6:
                            continue
                        for k3 in range(k2 + 1, 9):
                            if len(self.f[k3][j]['poss']) == 1 or len(self.f[k3][j]['poss']) > 6:
                                continue
                            for k4 in range(k3 + 1, 9):
                                if len(self.f[k4][j]['poss']) == 1 or len(self.f[k4][j]['poss']) > 6:
                                    continue
                                for k5 in range(k4 + 1, 9):
                                    if len(self.f[k5][j]['poss']) == 1 or len(self.f[k5][j]['poss']) > 6:
                                        continue
                                    digits = set(self.f[i][j]['poss']+self.f[k1][j]['poss']+self.f[k2][j]['poss']+self.f[k3][j]['poss']+self.f[k4][j]['poss']+self.f[k5][j]['poss'])
                                    if len(digits) == 6:
                                        for l in range(9):
                                            if l == i or l == k1 or l == k2 or l == k3 or l == k4 or l == k5:
                                                continue
                                            for p in digits:
                                                if p in self.f[l][j]['poss']:
                                                    self.f[l][j]['poss'].remove(p)
                                                    self.printA('naked6 removes '+str(p)+' von Zelle '+self.label[l]+str(j+1))
                                                    if len(self.f[l][j]['poss']) == 1:
                                                        self.f[l][j]['solved'] = True
                                        break

    def setti(self):

        for d in range(1, 10):
            for hv in range(2):
                self.s[d][hv] = {'v': 0, 'n': 0, 'vIndex': []}  # v: Anzahl vielleicht, n: Anzahl nein,
                                                                # vIndex: vielleicht Reihen/Spalten
            for i in range(9):
                found = 'n' # n=nein, s=sicher, v=vielleicht
                end = -1
                while end < 9:
                    start = end + 1
                    end = start
                    while end < 9 and not self.f[i][end]['schwarz']:
                        end += 1
                    if end < 9 and d == self.f[i][end]['poss'][0]:  # schwarzes Feld
                        found = 's'
                    # Strasse: von start bis end-1
                    if end < start + 1:  # Strasse mit Länge 0, dh. 'schwarz' bei end=9(schon iteriert)
                        if end == 9 and d == self.f[i][end - 1]['poss'][0]:  # schwarzes Feld
                            found = 's'
                        continue
                    min = 10
                    for j in range(start, end):
                        if self.f[i][j]['poss'][0] < min:
                            min = self.f[i][j]['poss'][0]
                    max = 0
                    for j in range(start, end):
                        if self.f[i][j]['poss'][-1] > max:
                            max = self.f[i][j]['poss'][-1]
                    # Prüfe, ob d von min bis max in Strasse start bis end-1 sicher vorkommt
                    for j in range(start, end):
                        if self.f[i][j]['solved'] and d == self.f[i][j]['poss'][0]:
                            found = 's'
                            break
                        elif d in self.f[i][j]['poss']:
                            found = 'v' # hier noch genauer werden: über Strassen ermitteln, ob nicht d 'sicher' ist
                            break
                    if found == 's':
                        break
                    elif found == 'v':
                        l = end - start         # Länge der Strasse
                        spread = max - min + 1  # wieviel digits in Strasse
                        puffer = spread - l     # digits-Bereich von 'sicher'
                        if min + puffer <= d and d <= max - puffer:
                            found == 's'
                        else:
                            self.s[d][0]['v'] += 1
                            self.s[d][0]['vIndex'].append(i)
                        break
                if found == 'n':
                    self.s[d][0]['n'] += 1

            for j in range(9):
                found = 'n'
                end = -1
                while end < 9:
                    start = end + 1
                    end = start
                    while end < 9 and not self.f[end][j]['schwarz']:
                        end += 1
                    if end < 9 and d == self.f[end][j]['poss'][0]:  # schwarzes Feld
                        found = 's'
                    # Strasse: von start bis end-1
                    if end < start + 1:  # Strasse mit Länge 0, dh. 'schwarz' bei end=9(schon iteriert)
                        if end == 9 and d == self.f[end - 1][j]['poss'][0]:  # schwarzes Feld
                            found = 's'
                        continue
                    min = 10
                    for i in range(start, end):
                        if self.f[i][j]['poss'][0] < min:
                            min = self.f[i][j]['poss'][0]
                    max = 0
                    for i in range(start, end):
                        if self.f[i][j]['poss'][-1] > max:
                            max = self.f[i][j]['poss'][-1]
                    # Prüfe, ob d von min bis max in Strasse start bis end-1 sicher vorkommt
                    for i in range(start, end):
                        if self.f[i][j]['solved'] and d == self.f[i][j]['poss'][0]:
                            found = 's'
                            break
                        elif d in self.f[i][j]['poss']:
                            found = 'v' # hier noch genauer werden: über Strassen ermitteln, ob nicht d 'sicher' ist
                            break
                    if found == 's':
                        break
                    elif found == 'v':
                        l = end - start         # Länge der Strasse
                        spread = max - min + 1  # wieviel digits in Strasse
                        puffer = spread - l     # digits-Bereich von 'sicher'
                        if min + puffer <= d and d <= max - puffer:
                            found == 's'
                        else:
                            self.s[d][1]['v'] += 1
                            self.s[d][1]['vIndex'].append(j)
                        break
                if found == 'n':
                    self.s[d][1]['n'] += 1

            # Auswertung Setti:
            #   Hn=horizontal,AnzahlNein, Hv=Horizontal,AnzahlVielleicht, Vn, Vv entsprechend für Vertikal
            #   Hn = Vv + Vn
            #   und Vv > 0, dann alle Vv sind Vn und alle Hv sind Hs (sicher)
            #   und Vv = 0, dann alle Hv sind Hs
            #   entsprechend für Vn = Hv + Hn
            if self.s[d][0]['n'] == self.s[d][1]['v'] + self.s[d][1]['n']:
                if self.s[d][1]['v'] > 0:
                    # Vv --> Vn
                    for j in self.s[d][1]['vIndex']:
                        for i in range(9):
                            if d in self.f[i][j]['poss']:
                                self.f[i][j]['poss'].remove(d)
                                self.printA('setti on '+str(d)+' removes '+str(d)+' von Zelle '+self.label[i]+str(j+1))
                                if len(self.f[i][j]['poss']) == 1:
                                    self.f[i][j]['solved'] = True
                if self.s[d][0]['v'] > 0:
                    # Hv --> Hs
                    for i in self.s[d][0]['vIndex']:
                        unique = 0
                        end = -1
                        while end < 9:
                            start = end + 1
                            end = start
                            while end < 9 and not self.f[i][end]['schwarz']:
                                end += 1
                            # Strasse: von start bis end-1
                            if end < start + 1:  # Strasse mit Länge 0
                                continue
                            min = 10
                            for j in range(start, end):
                                if self.f[i][j]['poss'][0] < min:
                                    min = self.f[i][j]['poss'][0]
                            max = 0
                            for j in range(start, end):
                                if self.f[i][j]['poss'][-1] > max:
                                    max = self.f[i][j]['poss'][-1]
                            if min <= d and d <= max:   # d ist sicher im range min bis max, zähle wie häufig
                                unique += 1
                        if unique == 1: # eleminiere ggfs. mit Len(Strasse) = end - start
                            end = -1
                            while end < 9:
                                start = end + 1
                                end = start
                                while end < 9 and not self.f[i][end]['schwarz']:
                                    end += 1
                               # Strasse: von start bis end-1
                                if end < start + 1:  # Strasse mit Länge 0
                                    continue
                                min = 10
                                for j in range(start, end):
                                    if self.f[i][j]['poss'][0] < min:
                                        min = self.f[i][j]['poss'][0]
                                max = 0
                                for j in range(start, end):
                                    if self.f[i][j]['poss'][-1] > max:
                                        max = self.f[i][j]['poss'][-1]
                                if min <= d and d <= max:
                                    for p in range(min, d - (end - start) + 1):
                                        for j in range(start, end):
                                            if p in self.f[i][j]['poss']:
                                                self.f[i][j]['poss'].remove(p)
                                                self.printA('setti on '+str(d)+' removes '+str(p)+' von Zelle '+self.label[i]+str(j+1))
                                                if len(self.f[i][j]['poss']) == 1:
                                                    self.f[i][j]['solved'] = True
                                    for p in (d + end - start, max + 1):
                                        for j in range(start, end):
                                            if p in self.f[i][j]['poss']:
                                                self.f[i][j]['poss'].remove(p)
                                                self.printA('setti on '+str(d)+' removes '+str(p)+' von Zelle '+self.label[i]+str(j+1))
                                                if len(self.f[i][j]['poss']) == 1:
                                                    self.f[i][j]['solved'] = True

            if self.s[d][1]['n'] == self.s[d][0]['v'] + self.s[d][0]['n']:
                if self.s[d][0]['v'] > 0:
                    # Hv --> Hn
                    for i in self.s[d][0]['vIndex']:
                        for j in range(9):
                            if d in self.f[i][j]['poss']:
                                self.f[i][j]['poss'].remove(d)
                                self.printA('setti on '+str(d)+' removes '+str(d)+' von Zelle '+self.label[i]+str(j+1))
                                if len(self.f[i][j]['poss']) == 1:
                                    self.f[i][j]['solved'] = True
                if self.s[d][1]['v'] > 0:
                    # Vv --> Vs
                    for j in self.s[d][1]['vIndex']:
                        unique = 0
                        end = -1
                        while end < 9:
                            start = end + 1
                            end = start
                            while end < 9 and not self.f[end][j]['schwarz']:
                                end += 1
                            # Strasse: von start bis end-1
                            if end < start + 1:  # Strasse mit Länge 0
                                continue
                            min = 10
                            for i in range(start, end):
                                if self.f[i][j]['poss'][0] < min:
                                    min = self.f[i][j]['poss'][0]
                            max = 0
                            for i in range(start, end):
                                if self.f[i][j]['poss'][-1] > max:
                                    max = self.f[i][j]['poss'][-1]
                            if min <= d and d <= max:   # d ist sicher im range min bis max, zähle wie häufig
                                unique += 1
                        if unique == 1: # eleminiere ggfs. mit Len(Strasse) = end - start
                            end = -1
                            while end < 9:
                                start = end + 1
                                end = start
                                while end < 9 and not self.f[end][j]['schwarz']:
                                    end += 1
                                # Strasse: von start bis end-1
                                if end < start + 1:  # Strasse mit Länge 0
                                    continue
                                min = 10
                                for i in range(start, end):
                                    if self.f[i][j]['poss'][0] < min:
                                        min = self.f[i][j]['poss'][0]
                                max = 0
                                for i in range(start, end):
                                    if self.f[i][j]['poss'][-1] > max:
                                        max = self.f[i][j]['poss'][-1]
                                if min <= d and d <= max:
                                    for p in range(min, d - (end - start) + 1):
                                        for i in range(start, end):
                                            if p in self.f[i][j]['poss']:
                                                self.f[i][j]['poss'].remove(p)
                                                self.printA('setti on '+str(d)+' removes '+str(p)+' von Zelle '+self.label[i]+str(j+1))
                                                if len(self.f[i][j]['poss']) == 1:
                                                    self.f[i][j]['solved'] = True
                                    for p in (d + end - start, max + 1):
                                        for i in range(start, end):
                                            if p in self.f[i][j]['poss']:
                                                self.f[i][j]['poss'].remove(p)
                                                self.printA('setti on '+str(d)+' removes '+str(p)+' von Zelle '+self.label[i]+str(j+1))
                                                if len(self.f[i][j]['poss']) == 1:
                                                    self.f[i][j]['solved'] = True

    def fish2(self):
        # Sucht nach einem Digit, der in zwei Zeilen genau zweimal auftaucht, in denselben Spalten
        #   dann ist der Digit in den restlichen Positionen der Spalten eleminierbar.
        # Entsprechend für zwei Spalten ...
        # Auftauchen des Digits muss sicher sein: hierzu wird Ergebnis des letzten Setti verwendet
        for d in range(1, 10):
            double = []  # Elemente: Zeile und Liste mit den beiden Spalten
            for i in range(9):
                if i in self.s[d][0]['vIndex']:
                    continue
                isDouble = 0
                rDouble = []
                for j in range(9):
                    if d in self.f[i][j]['poss']:
                        isDouble += 1
                        rDouble.append(j)
                if isDouble == 2:
                    double.append([i, rDouble])
            for k1 in range(len(double)):
                for k2 in range(k1 + 1, len(double)):
                    if double[k1][1] == double[k2][1]:
                        for j in double[k1][1]:
                            for k in range(9):
                                if k == double[k1][0] or k == double[k2][0]:
                                    continue
                                if d in self.f[k][j]['poss']:
                                    self.f[k][j]['poss'].remove(d)
                                    self.printA('fish2 removes '+str(d)+' von Zelle '+self.label[k]+str(j+1))
                                    if len(self.f[k][j]['poss']) == 1:
                                        self.f[k][j]['solved'] = True
        for d in range(1, 10):
            double = [] # Elemente: Spalte und Liste mit den beiden Zeilen
            for j in range(9):
                if j in self.s[d][1]['vIndex']:
                    continue
                isDouble = 0
                rDouble = []
                for i in range(9):
                    if d in self.f[i][j]['poss']:
                        isDouble += 1
                        rDouble.append(i)
                if isDouble == 2:
                    double.append([j, rDouble])
            for k1 in range(len(double)):
                for k2 in range(k1+1, len(double)):
                    if double[k1][1] == double[k2][1]:
                        for i in double[k1][1]:
                            for k in range(9):
                                if k == double[k1][0] or k == double[k2][0]:
                                    continue
                                if d in self.f[i][k]['poss']:
                                    self.f[i][k]['poss'].remove(d)
                                    self.printA('fish2 removes '+str(d)+' von Zelle '+self.label[i]+str(k+1))
                                    if len(self.f[i][k]['poss']) == 1:
                                        self.f[i][k]['solved'] = True

    def fish3(self):
        # Sucht nach einem Digit, der in drei Zeilen zweimal oder dreimal auftaucht, in denselben Spalten
        #   dann ist der Digit in den restlichen Positionen der Spalten eleminierbar.
        # Entsprechend für drei Spalten ...
        # Auftauchen des Digits muss sicher sein: hierzu wird Ergebnis des letzten Setti verwendet
        for d in range(1, 10):
            triple = []  # Elemente: Zeile und Liste mit den drei Spalten
            for i in range(9):
                if i in self.s[d][0]['vIndex']:
                    continue
                isTriple = 0
                rTriple = []
                for j in range(9):
                    if d in self.f[i][j]['poss']:
                        isTriple += 1
                        rTriple.append(j)
                if isTriple == 2 or isTriple == 3:
                    triple.append([i, rTriple])
            for k1 in range(len(triple)):
                for k2 in range(k1 + 1, len(triple)):
                    for k3 in range(k2 + 1, len(triple)):
                        if len(set(triple[k1][1]) | set(triple[k2][1]) | set(triple[k3][1])) == 3:
                            for j in triple[k1][1]:
                                for k in range(9):
                                    if k == triple[k1][0] or k == triple[k2][0] or k == triple[k3][0]:
                                        continue
                                    if d in self.f[k][j]['poss']:
                                        self.f[k][j]['poss'].remove(d)
                                        self.printA('fish3 removes '+str(d)+' von Zelle '+self.label[k]+str(j+1))
                                        if len(self.f[k][j]['poss']) == 1:
                                            self.f[k][j]['solved'] = True
        for d in range(1, 10):
            triple = []  # Elemente: Spalte und Liste mit den drei Zeilen
            for j in range(9):
                if j in self.s[d][1]['vIndex']:
                    continue
                isTriple = 0
                rTriple = []
                for i in range(9):
                    if d in self.f[i][j]['poss']:
                        isTriple += 1
                        rTriple.append(i)
                if isTriple == 2 or isTriple == 3:
                    triple.append([j, rTriple])
            for k1 in range(len(triple)):
                for k2 in range(k1 + 1, len(triple)):
                    for k3 in range(k2 + 1, len(triple)):
                        if len(set(triple[k1][1]) | set(triple[k2][1]) | set(triple[k3][1])) == 3:
                            for i in triple[k1][1]:
                                for k in range(9):
                                    if k == triple[k1][0] or k == triple[k2][0] or k == triple[k3][0]:
                                        continue
                                    if d in self.f[i][k]['poss']:
                                        self.f[i][k]['poss'].remove(d)
                                        self.printA('fish3 removes '+str(d)+' von Zelle '+self.label[i]+str(k+1))
                                        if len(self.f[i][k]['poss']) == 1:
                                            self.f[i][k]['solved'] = True

    def fish4(self):
        # Sucht nach einem Digit, der in vier Zeilen zwei, drei oder viermal auftaucht, in denselben Spalten
        #   dann ist der Digit in den restlichen Positionen der Spalten eleminierbar.
        # Entsprechend für vier Spalten ...
        # Auftauchen des Digits muss sicher sein: hierzu wird Ergebnis des letzten Setti verwendet
        for d in range(1, 10):
            vier = []  # Elemente: Zeile und Liste mit den vier Spalten
            for i in range(9):
                if i in self.s[d][0]['vIndex']:
                    continue
                is4 = 0
                r4 = []
                for j in range(9):
                    if d in self.f[i][j]['poss']:
                        is4 += 1
                        r4.append(j)
                if is4 == 2 or is4 == 3 or is4 == 4:
                    vier.append([i, r4])
            for k1 in range(len(vier)):
                for k2 in range(k1 + 1, len(vier)):
                    for k3 in range(k2 + 1, len(vier)):
                        for k4 in range(k3 + 1, len(vier)):
                            if len(set(vier[k1][1]) | set(vier[k2][1]) | set(vier[k3][1]) | set(vier[k4][1])) == 4:
                                for j in vier[k1][1]:
                                    for k in range(9):
                                        if k == vier[k1][0] or k == vier[k2][0] or k == vier[k3][0] or k == vier[k4][0]:
                                            continue
                                        if d in self.f[k][j]['poss']:
                                            self.f[k][j]['poss'].remove(d)
                                            self.printA('fish4 removes '+str(d)+' von Zelle '+self.label[k]+str(j+1))
                                            if len(self.f[k][j]['poss']) == 1:
                                                self.f[k][j]['solved'] = True
        for d in range(1, 10):
            vier = []  # Elemente: Zeile und Liste mit den vier Spalten
            for j in range(9):
                if j in self.s[d][1]['vIndex']:
                    continue
                is4 = 0
                r4 = []
                for i in range(9):
                    if d in self.f[i][j]['poss']:
                        is4 += 1
                        r4.append(i)
                if is4 == 2 or is4 == 3 or is4 == 4:
                    vier.append([j, r4])
            for k1 in range(len(vier)):
                for k2 in range(k1 + 1, len(vier)):
                    for k3 in range(k2 + 1, len(vier)):
                        for k4 in range(k3 + 1, len(vier)):
                            if len(set(vier[k1][1]) | set(vier[k2][1]) | set(vier[k3][1]) | set(vier[k4][1])) == 4:
                                for i in vier[k1][1]:
                                    for k in range(9):
                                        if k == vier[k1][0] or k == vier[k2][0] or k == vier[k3][0] or k == vier[k4][0]:
                                            continue
                                        if d in self.f[i][k]['poss']:
                                            self.f[i][k]['poss'].remove(d)
                                            self.printA('fish4 removes '+str(d)+' von Zelle '+self.label[i]+str(k+1))
                                            if len(self.f[i][k]['poss']) == 1:
                                                self.f[i][k]['solved'] = True

    def guess2(self, tryKleinere):
        # Wird gerufen, wenn sonst nicht lösbar:
        #   suche 1. Zelle mit 2 Possibilities (Tupel),
        #   nimm kleinere davon als Vermutung, bei tryKleinere = True; sonst größere
        #   und schaue ob lösbar und fehlerfrei.
        #   Wenn mit Fehler, dann Vermutung falsch, also andere Possibility richtig --> rekursiver Aufruf
        #   Wenn nicht lösbar, versuche mit anderen Tupel
        for i in range(9):
            for j in range(9):
                if len(self.f[i][j]['poss']) == 2:
                    itCount = self.it
                    fG = copy.deepcopy(self.f)
                    if tryKleinere:
                        d = self.f[i][j]['poss'][1]
                    else:
                        d = self.f[i][j]['poss'][0]
                    self.f[i][j]['poss'].remove(d)
                    self.f[i][j]['solved'] = True
                    self.printA('guess2 removes ' + str(d) + ' von Zelle ' + self.label[i] + str(j + 1))
                    try:
                        self.solve()
                        if self.anzSolved == 81:
                            return
                        self.printA('guess2 konnte mit dem Versuch Str8ts nicht lösen: rückgängig machen')
                        self.f = fG
                        self.it = itCount
                        # Lösche Layout Files des Trials, der nicht solvte
                        while True:
                            file = self.fileStamm + str(itCount) + '.png'
                            if os.path.isfile(file):
                                os.unlink(file)
                                itCount += 1
                            else:
                                break
                    except:
                        self.printA('guess2 lief auf Fehler, also Annahme falsch')
                        self.f = fG
                        self.it = itCount
                        # Lösche falsche Layout Files
                        while True:
                            file = self.fileStamm + str(itCount) + '.png'
                            if os.path.isfile(file):
                                os.unlink(file)
                                itCount += 1
                            else:
                                break
                        if tryKleinere:
                            d = self.f[i][j]['poss'][0]
                        else:
                            d = self.f[i][j]['poss'][1]
                        self.f[i][j]['poss'].remove(d)
                        self.f[i][j]['solved'] = True
                        self.printA('guess2 removes ' + str(d) + ' von Zelle ' + self.label[i] + str(j + 1))
                        self.solve()
                        if self.anzSolved == 81:
                            return
                        else:
                            self.printS(setti=True)
                            self.guess2(tryKleinere)   # rekursiver Aufruf
                            return

    def guess3(self, tryTripel=0):
        # Wird gerufen, wenn sonst nicht lösbar:
        #   suche 1. Zelle mit 3 Possibilities (Tripel),
        #   nimm kleinste davon als Vermutung, bei tryTripel = 0; sonst mittelere (1), große (2)
        #   und schaue ob lösbar und fehlerfrei.
        #   Wenn mit Fehler, dann Vermutung falsch, also andere Possibility richtig
        #       --> weiter Aufruf von solve und ggfs guess2
        #   Wenn nicht lösbar, versuche mit anderen Tripel
        for i in range(9):
            for j in range(9):
                if len(self.f[i][j]['poss']) == 3:
                    itCount = self.it
                    fG = copy.deepcopy(self.f)
                    d = self.f[i][j]['poss'][tryTripel]
                    self.f[i][j]['poss'].remove(d)
                    self.printA('guess3 removes ' + str(d) + ' von Zelle ' + self.label[i] + str(j + 1))
                    try:
                        self.solve()
                        if self.anzSolved == 81:
                            return
                        self.printA('guess3 konnte mit dem Versuch Str8ts nicht lösen: rückgängig machen')
                        self.f = fG
                        self.it = itCount
                        # Lösche Layout Files des Trials, der nicht solvte
                        while True:
                            file = self.fileStamm + str(itCount) + '.png'
                            if os.path.isfile(file):
                                os.unlink(file)
                                itCount += 1
                            else:
                                break
                    except:
                        self.printA('guess3 lief auf Fehler, also Annahme falsch')
                        self.f = fG
                        self.it = itCount
                        # Lösche falsche Layout Files
                        while True:
                            file = self.fileStamm + str(itCount) + '.png'
                            if os.path.isfile(file):
                                os.unlink(file)
                                itCount += 1
                            else:
                                break
                        self.f[i][j]['poss'] = [d]
                        self.f[i][j]['solved'] = True
                        self.printA('guess3 solves Zelle ' + self.label[i] + str(j + 1) + ' mit ' + str(d))
                        self.solve()
                        if self.anzSolved == 81:
                            return
                        else:
                            self.printS(setti=True)
                            self.guess2(True)
                            if self.anzSolved == 81:
                                return
                            else:
                                self.printS(setti=True)
                                self.guess2(False)
                            return

    def printA(self, s):
        # Druckt Kommentare über Algorithmus-Lösungen, gesteuert über: self.printLevel
        #   Möglichkeiten: nie, gering, viel, alles
        self.anzPrintA += 1
        caller = inspect.stack()[1][3]

        if self.printLevel == 'gering':
            if caller=='guess2' or caller=='fish4' or caller=='setti' or caller=='guess3' or caller=='naked6':
                print(s)
        elif self.printLevel == 'viel':
            if caller != 'algZahlFix':
                print(s)
        elif self.printLevel == 'alles':
            print(s)

    def printS(self, setti=False):
        # Druckt Layout. Beim 1. Mal ohne Possibilities, danach mit.
        #   Zählt Druckversion hoch und ermittelt Anzahl solved Cells

        sizeQ = 50
        start = sizeQ
        end = start + 9 * sizeQ
        sizeDraw = end + 4 * sizeQ

        sFont = ImageFont.truetype('Library/Fonts/Arial Bold.ttf', int(sizeQ / 4))
        mFont = ImageFont.truetype('Library/Fonts/Arial Bold.ttf', int(0.25 * sizeQ))
        lFont = ImageFont.truetype('Library/Fonts/Arial Bold.ttf', int(0.7 * sizeQ))

        im = Image.new('RGBA', (sizeDraw, sizeDraw), 'white')
        draw = ImageDraw.Draw(im)

        def grid():
            # Male Linien für 9*9 Quadrat
            for x in range(start, end + sizeQ, sizeQ):
                draw.line([(x, start), (x, end)], fill = 'black')

            for y in range(start, end + sizeQ, sizeQ):
                draw.line([(start, y), (end, y)], fill = 'black')

            # Ränder mit Labels A-J und 1-9
            for i in range(9):
                draw.text((start+i*sizeQ+0.4*sizeQ, start-sizeQ/3), str(i+1), fill='black', font=sFont)

            for i in range(9):
                draw.text((start-0.4*sizeQ, start+i*sizeQ+sizeQ/3), str8ts.label[i], fill='black', font=sFont)

        def quadrat(x, y, i=0, schwarz=False, p=[]):
            # Male Zelle:
            #   B3, dann x=3 und y='B'
            #   mit Zahl i, keine Zahl bei i=0
            #   in Schwarz, wenn schwarz=True
            yNum = str8ts.label.index(y)

            if schwarz:
                color = 'black'
                zahlColor = 'white'
            else:
                color = 'white'
                zahlColor = 'black'

            draw.rectangle((start+(x-1)*sizeQ, start+yNum*sizeQ, start+x*sizeQ, start+(yNum+1)*sizeQ), fill=color)

            if i != 0:
                draw.text((start+(x-1)*sizeQ+0.3*sizeQ, start+yNum*sizeQ+0.1*sizeQ), str(i), fill=zahlColor, font=lFont)
            elif p != []:
                position = 0
                l = len(p)
                for j in range(1, 10):
                    if j == p[position]:
                        relX = 0.1 + ((j-1)%3) * 0.3
                        relY = 0.1+((j-1)//3)*0.3
                        draw.text((start+(x-1)*sizeQ+relX*sizeQ, start+yNum*sizeQ+relY*sizeQ), str(j), fill=zahlColor, font=sFont)
                        if position == l - 1:
                            break
                        else:
                            position += 1

        if self.it == 0:
            quPoss = False

            # Lösche alte Layout Files
            i = 0
            while True:
                file = self.fileStamm + str(i) + '.png'
                if os.path.isfile(file):
                    os.unlink(file)
                    i +=1
                else:
                    break
        else:
            quPoss = True

        self.anzSolved = 0

        for i in range(9):
            for j in range(9):
                if self.f[i][j]['solved']:
                    self.anzSolved += 1
                    quadrat(j+1, str8ts.label[i], i=self.f[i][j]['poss'][0], schwarz=self.f[i][j]['schwarz'])
                elif quPoss:
                    quadrat(j+1, str8ts.label[i], p=self.f[i][j]['poss'])

        grid()

        if setti:
            for d in range(1, 10):
                draw.text((start, end+0.3*d*sizeQ), str(d)+': H '+str(self.s[d][0]), fill='black', font=mFont)
                draw.text((start+5*sizeQ, end+0.3*d*sizeQ), '   V '+str(self.s[d][1]), fill='black', font=mFont)

        print('Anzahl solved cells: ' + str(self.anzSolved) + '   Diagramm : ' + str(self.it))
        im.save(self.fileStamm + str(self.it) + '.png')
        self.it += 1

    def inputS(self):
        # Einlesen von Input
        print('''Gib Str8ts Quadrate ein, Format: A1,3,s (Feld A1 mit Zahl 3 in Schwarz), bzw. Zahl 0, bzw. w = Weiss,
              End für Ende''')

        while True:
            s = input('Quadrat : \n')

            if s == 'End':
                break

            syn = re.findall(r'[A-HJ][1-9],[0-9],[SW]', s.upper())
            if syn == []:
                print('Syntax falsch, bitte erneute Eingabe.\n')
                continue

            s = syn[0]

            if s[5] == 'S':
                obS = True
            else:
                obS = False
                if s[3] == '0':
                    print('Eingabe Zahl 0 bei Weiss falsch, bitte erneute Eingabe.\n')
                    continue

            self.f[str8ts.label.index(s[0])][int(s[1])-1] = {'solved': True, 'poss': [int(s[3])], 'schwarz': obS}

    def solve(self):
        lastAnzPrintA = 0
        while self.anzPrintA > lastAnzPrintA:
            lastAnzPrintA = self.anzPrintA
            self.strandedSeq()
            self.algZahlFix()
            self.printS()
            self.strasseMinMax()
            self.algZahlFix()
            self.printS()
            self.requiredDigits()
            self.algZahlFix()
            self.printS()
            self.strasse23()
            self.algZahlFix()
            self.printS()
            self.naked2()
            self.algZahlFix()
            self.printS()
            self.naked3()
            self.algZahlFix()
            self.printS()
            self.setti()
            self.algZahlFix()
            self.printS()
            self.fish2()
            self.algZahlFix()
            self.printS()
            self.fish3()
            self.algZahlFix()
            self.printS()
            self.fish4()
            self.algZahlFix()
            self.printS()
            self.naked4()
            self.algZahlFix()
            self.printS()
            self.naked5()
            self.algZahlFix()
            self.printS()
            self.naked6()
            self.algZahlFix()
            self.printS()

#main
os.chdir('/Users/kai/Documents/Python/Str8ts')

o = str8ts()

o.printLevel = 'gering'
o.inputS()
o.printS()
o.algZahlFix()
o.printS()

o.solve()

if o.anzSolved < 81:
    o.printS(setti=True)
    o.guess2(True)
if o.anzSolved < 81:
    o.printS(setti=True)
    o.guess2(False)

if o.anzSolved < 81:
    o.printS(setti=True)
    o.guess3(0)
if o.anzSolved < 81:
    o.printS(setti=True)
    o.guess3(1)
if o.anzSolved < 81:
    o.printS(setti=True)
    o.guess3(2)
