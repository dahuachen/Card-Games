import itertools
import random

class Card:
    diamonds, clubs = '\u2662','\u2663'
    hearts, spades = '\u2661', '\u2660'
    suits = (diamonds, clubs, hearts, spades)
    ranks = ('3','4','5','6','7','8','9','10',
             'J','Q','K','A','2')
    
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
    
    def __str__(self):
        return self.rank + self.suit
    
    def __repr__(self):
        return self.__str__()
    
    # comparing cards: compare rank first, then suit as a tiebreaker
    def __eq__(self, other):
        return self.rank == other.rank and self.suit == other.suit
    
    def __lt__(self,other):
        r1,r2 = Card.ranks.index(self.rank), Card.ranks.index(other.rank)
        s1,s2 = Card.suits.index(self.suit), Card.suits.index(other.suit)
        return (r1 < r2) or (r1 == r2 and s1 < s2)
    
    def __le__(self, other):
        return self < other or self == other
    
    def __gt___(self, other):
        return not self <= other
    
    def __ge__(self, other):
        return not self < other
    
    # Make Card objects hashable
    def __hash__(self):
        return hash((self.rank,self.suit))
    
class Deck:
    def __init__(self):
        self.cards = [Card(rank,suit) for rank in Card.ranks 
                      for suit in Card.suits]
        self.shuffle()
    
    def __repr__(self):
        return str(self.cards)
    
    def cards(self):
        return self.cards
    
    def shuffle(self):
        random.shuffle(self.cards)

class PokerHands:
    def __init__(self,hand):
        self.hand = sorted(hand)
        self.ranks = {rank:0 for rank in Card.ranks}
        self.suits = {suit:0 for suit in Card.suits}
        for card in self.hand:
            self.ranks[card.rank] += 1
            self.suits[card.suit] += 1
    
    # used to simplify classification of singles, pairs, triples
    def sameRank(self,n):
        tuples = []
        rks = [r for r in self.ranks if self.ranks[r] > n-1]
        for rank in rks:
            cards = sorted([c for c in self.hand if c.rank == rank])
            c = list(itertools.combinations(cards,n))
            for x in c:
                tuples.append(x)
        return tuples
    
    def singles(self):
        s = self.sameRank(1)
        return s
    
    def pairs(self):
        p = self.sameRank(2)
        return p
    
    def triples(self):
        t = self.sameRank(3)
        return t
    
    # returns all straights, including straight flushes
    def allStraights(self):
        # starting ranks of possible straights
        starts = []
        l = list(self.ranks.values())
        for i in range(len(l)-4):
            if 0 not in l[i:i+5]:
                s = list(self.ranks.keys())[i]
                starts.append(s)
        straights = []
        for s in starts:
            for c in self.hand:
                if c.rank == s:
                    # include rank up to but not including this rank
                    end = Card.ranks.index(s) + 4
                    endrank = Card.ranks[end]
                    i = self.hand.index(c)
                    # find last card that can be used for a straight
                    endcds = [c for c in self.hand if c.rank == endrank]
                    j = self.hand.index(endcds[::-1][0])
                    
                    st = self.hand[i:j+1]
                    combs = list(itertools.combinations(st,5))
                    for comb in combs:
                        # valid straight if no duplicate ranks
                        valid = True
                        for i in range(4):
                            if comb[i].rank == comb[i+1].rank:
                                valid = False
                        if valid:
                            straights.append(comb)
        
        # exceptions are A-2-3-4-5 and 2-3-4-5-6
        l = l[11:]+l[:11] # reorder ranks to A-2-3-...
        starts1 = []
        for i in range(2):
            if 0 not in l[i:i+5]:
                s = list(self.ranks.keys())[i+11]
                starts1.append(s)
        for s in starts1:
            for c in self.hand:
                if c.rank == s:
                    end = Card.ranks.index(s) - 9
                    endrank = Card.ranks[end]
                    possible1 = [x for x in self.hand if 
                                 Card.ranks.index(x.rank) >= Card.ranks.index(c.rank)]
                    possible2 = [y for y in self.hand if 
                                 Card.ranks.index(y.rank) <= end]
                    possible = possible1 + possible2
                    combs = list(itertools.combinations(possible,5))
                    for comb in combs:
                        valid = True
                        for i in range(4):
                            if comb[i].rank == comb[i+1].rank:
                                valid = False
                        if valid:
                            comb = tuple(sorted(comb))
                            straights.append(comb)
        return straights
    
    def straights(self):
        # make straights mutually exclusive from straight flushes
        return [s for s in self.allStraights() if s not in self.allFlushes()]
    
    # all flushes, including straight flushes
    def allFlushes(self):
        fsuits = [s for s in self.suits if self.suits[s] >= 5]
        # nested list comprehension - group by suit
        f = [sorted([c for c in self.hand if c.suit == i]) for i in fsuits]
        ff = [list(itertools.combinations(x,5)) for x in f]
        flushes = [f for i in range(len(ff)) for f in ff[i]]
        return flushes
    
    def flushes(self):
        # make flushes mutually exclusive from straight flushes
        return [f for f in self.allFlushes() if f not in self.allStraights()]

    def fullhouses(self):
        trip = [r for r in self.ranks if self.ranks[r] >= 3]
        trips = []
        for t in trip:
            c = sorted([c for c in self.hand if c.rank == t])
            d = list(itertools.combinations(c,3))
            for e in d:
                trips.append(e)
        fh = []
        for t in trips:
            # the cards in the hand other than those in the triple
            h = sorted([c for c in self.hand if not c in t])
            hranks = {rank:0 for rank in Card.ranks}
            for card in h:
                hranks[card.rank] += 1
            # all the ranks that can be used for pairs
            p = [x for x in hranks if hranks[x] > 1]
            for rank in p:
                cards = [c for c in h if c.rank == rank]
                combs = list(itertools.combinations(cards,2))
                for x in combs:
                    # construct a full house
                    fh.append(t+x)
        return fh
    
    def fourofakinds(self):
        # ranks in hand that appear 4 times
        four = [r for r in self.ranks if self.ranks[r] == 4]
        # tuples of 4 cards with same rank
        fours = []
        for f in four:
            c = sorted([c for c in self.hand if c.rank == f])
            fours.append(tuple(c))
        foak = []
        for f in fours:
            h = sorted([c for c in self.hand if not c in f])
            for x in h:
                # construct a four-of-a-kind
                foak.append(f+tuple([x]))
        return foak
    
    def straightflushes(self):
        allstrs = self.allStraights()
        strs = self.straights()
        sf = [x for x in allstrs if not x in strs]
        return list(set(sf))
                        
    def order(self):
        o = [self.straightflushes(), self.fourofakinds(), self.fullhouses(),
             self.flushes(), self.straights(), self.triples(),
             self.pairs(), self.singles()]
        return o
    
    def validplays(self, played):
        l = len(played)
        hands = self.order()
        if l == 1:
            valid = [v for v in hands[7] if v[0] > played[0]]
        if l == 2:
            valid = [v for v in hands[6] if max(v) > max(played)]
        if l == 3:
            valid = [v for v in hands[5] if max(v) > max(played)]
        if l == 5:
            valid = []
            # find what kind of hand p is
            p = PokerHands(played)
            p = p.order()[0:5]
            for i in p:
                if i != []:
                    # n will determine type of 5-card hand
                    n = p.index(i)
                    break
            if n == 0: # straight flushes
                for x in hands[0]:
                    if max(x) > max(played):
                        valid.append(x)
            if n == 1: # four-of-a-kinds
                valid += hands[0]
                for x in hands[1]:
                    if x[0] > played[0]:
                        valid.append(x)
            if n == 2: # full houses
                valid = valid + hands[0] + hands[1]
                for x in hands[2]:
                    if x[0] > played[0]:
                        valid.append(x)
            if n == 3: # flushes
                for i in range(3):
                    valid += hands[i]
                psuit = played[0].suit
                ps = Card.suits.index(psuit)
                for x in hands[3]:
                    s = Card.suits.index(x[0].suit)
                    if s > ps:
                        valid.append(x)
                    if s == ps:
                        if max(x) > max(played):
                            valid.append(x)
            
            if n == 4: # straights
                for i in range(4):
                    valid += hands[i]
                for x in hands[4]:
                    if max(x) > max(played):
                        valid.append(x)
        return valid
        
class Player:
    def __init__(self, name, ptype):
        self.name = name
        self.type = ptype
        self.hand = []
        self.played = []
    
    # sort hand by card value
    def sorthand(self):
        hlen = len(self.hand)
        for j in range(1, hlen):
            x = self.hand[j]
            i = j - 1
            while i >= 0 and self.hand[i] > x:
                self.hand[i+1] = self.hand[i]
                i -= 1
            self.hand[i+1] = x
    
    # reset hand
    def resetHand(self):
        self.hand = []
        self.played = []
    
    # add cards to hand
    def addCards(self,deck,cards):
        self.hand += cards
        deck.cards = [c for c in deck.cards if not c in cards]
        self.sorthand()
    
    # play cards onto field
    def play(self,cards,field):
        self.hand = [c for c in self.hand if not c in cards]
        field += (cards,)
        self.played += (cards,)
        print("{} played {}".format(self.name,cards))

    # converts input into cards
    def validInput(self):
        while True:
            i = input("Please choose a valid move: ")
            if i == "pass":
                break
            
            s = i.replace('10','T')
            l = len(s)
            if l > 10 or l%2 == 1: 
                print("Invalid move")
                continue
            ranks = [s[i] for i in range(l) if i%2 == 0]
            for r in ranks:
                if r == 'T':
                    i = ranks.index('T')
                    ranks[i] = '10'

            invRank = False
            for r in ranks:
                if not r in Card.ranks:
                    invRank = True
                    break
            if invRank == True:
                print("Invalid move")
                continue

            suits = [s[i] for i in range(l) if i%2 == 1]
            invSuit = False
            for x in suits:
                if not x in ['d','c','h','s']:
                    invSuit = True
                    break
            if invSuit == True:
                print("Invalid move")
                continue

            d = {'d':'\u2662', 'c':'\u2663','h':'\u2661','s':'\u2660'}
            suits = [d[s[j]] for j in range(l) if j%2 == 1]
            
            cards = sorted([Card(r,s) for r,s in zip(ranks,suits)])
            p = PokerHands(self.hand)
            po = p.order()

            valid = False

            for i in po:
                for j in i:
                    if set(j) == set(cards):
                        cards = j
                        valid = True
                        
            if valid == True:
                return cards
            else:
                print("Invalid move")
                continue
        return []
    
    # make a move
    def move(self,field):
        poker = PokerHands(self.hand)
        order = poker.order()
        d,c,h,s = Card.suits
        
        if field == []:
            if self.type == "Human":
                print("You go first!")
                print("Your hand:", self.hand)
                vI = self.validInput()
                while not Card('3',d) in vI:
                    print("You must use the 3 of diamonds.")
                    print("Make a valid move.")
                    vI = self.validInput()
                self.play(vI,field)
                return
            
            if self.type == "Computer":
                for i in order:
                    for j in i:
                        if Card('3',d) in j:
                            self.play(j,field)
                            return
                        
        v = poker.validplays(field[-1])
        
        if self.type == "Human":
            if field[-1] in self.played:
                print("Your hand:", self.hand)
                print("You get a free turn!")
                self.play(self.validInput(),field)
                return
            
            if v == []:
                print("You cannot play anything. Pass.")
                return
            
            print("Your hand:", self.hand)
            print("Your turn!")
            while True:
                x = self.validInput()
                if x == []:
                    print("You pass.")
                    return
                if x in v:
                    break
                else:
                    print("Invalid move")
            self.play(x,field)
        
        if self.type == "Computer":
            if field[-1] in self.played:
                for i in order[::-1]:
                    if i != []:
                        self.play(i[0],field) 
                        return
            if v == []:
                print("%s passes." % self.name)
            else:
                # play the first available hand
                self.play(v[0],field)

class BigTwo:
# Also known as Big Deuce, Chinese Poker and other names
    def __init__(self):
        self.players = []
        self.field = []
        
    def play(self):
        print("Let's Play Big Two! For the full rules, see the writeup.")
        message = '''Key: 
        Suits: d = diamonds, c = clubs, h = hearts, s = spades
        Ranks: (lowest to highest) 3,4,5,6,7,8,9,10,J,Q,K,A,2
        Example: Entering 'Ah2dQsJcKh' is the equivalent of playing the
        straight J\u2663Q\u2660K\u2661A\u26612\u2662
        The order of the input of the cards does not matter. 
        
        Enter "pass" to pass your turn.
        '''
        print(message)
        # create players
        if self.players == []:
            self.players.append(Player("You","Human"))
            for j in range(1,4):
                self.players.append(Player("Python{}".format(str(j)),"Computer"))
        
        def victory(p):
            if p.hand == []:
                return True
            return False
        
        # deal out cards
        d = Deck()
        for p in self.players:
            p.addCards(d,d.cards[:13])
        
        # announce the order of play
        for p in self.players:
            if Card('3',Card.diamonds) in p.hand:
                order = [p]+[pl for pl in self.players if pl != p]
                names = [p.name for p in order]
                print("The order of play will be", names)
                break
                
        # end of game
        gameEnd = False
        
        while gameEnd == False:
            for i in range(4):
                order[i].move(self.field)
                if victory(order[i]):
                    if order[i].type == "Computer":
                        print("{} wins!".format(order[i].name))
                    else:
                        print("You win!")
                    gameEnd = True
                    break
        
        answer = input("Would you like to play again? yes - y, no - n")
        if answer not in ("y","n"):
            print("Invalid answer. Goodbye!")
        else:
            if answer == "y":
                for p in self.players:
                    p.resetHand()
                self.field = []
                self.play();
            if answer == "n":
                print("Thanks for playing!")

