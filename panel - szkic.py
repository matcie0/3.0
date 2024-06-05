

class panel:
    """ 
    Klasa obsługująca rysowanie wykresów, pokazujących liczbę zdobytych punktów
    """

    def __init__(self, przedmioty, punkty):
        """
        Odczytanie danych z pliku, utworzenie z nich wykresu
        """

        self.punkty=punkty
        self.przedmioty=przedmioty
        nazwy_przedmiotow=[]
        ile_punktow=[]

        with open('sumowane_punkty.txt','r') as file:
            self.slownik=file.read()

        for przedmioty,punkty in self.slownik.items():
            nazwy_przedmiotow.append(przedmioty)
            ile_punktow.append(punkty)

        ile_wykresow=len(nazwy_przedmiotow)

        for i in ile_wykresow:
            plt.xlim(0,2) #oś OX
            plt.ylim((0,100)) #oś OY
            plt.axhline(0,color='black') 
            plt.grid()
            aktualna_nazwa=przedmiot(i)
            aktualne_punkty=punkty(i)
            plt.xlabel('aktualna_nazwa')
            plt.ylabel('aktualne_punkty')   
            plt.bar(przedmioty(i),punkty(i)) 
            plt.show()    


            
              

        