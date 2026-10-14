# reguły edycji: (ylo,yhi,xlo,xhi,kx,ky,param) w znormalizowanych współrz. glifu (y: 1 = wys. wersalika)
def A_rules(tag, W_over_H, slope):
    # poprzeczka A: krawędź dolna (y~0.2/0.26) i górna (y~0.36/0.40) przesuwane wzdłuż nóg
    k = slope * W_over_H
    lo, hi = (0.15, 0.30), (0.33, 0.45)
    return [(*lo, 0.0, 0.5,  k, 1, tag+"bar_lo"), (*lo, 0.5, 1.0, -k, 1, tag+"bar_lo"),
            (*hi, 0.0, 0.5,  k, 1, tag+"bar_hi"), (*hi, 0.5, 1.0, -k, 1, tag+"bar_hi")]
def E_rules(tag):
    return [(0.39, 0.62, -1, 2, 0, 1, tag+"mid"),            # środkowa poprzeczka w pionie
            (0.39, 0.62, 0.5, 2, 1, 0, tag+"midlen"),        # długość środkowej
            (0.75, 0.90, 0.1, 1.1, 0, 1, tag+"topin"),       # dolna krawędź górnej belki
            (0.10, 0.25, 0.1, 1.1, 0, 1, tag+"botin"),       # górna krawędź dolnej belki
            (0.39, 0.46, -1, 2, 0, 1, tag+"midthk")]         # grubość środkowej (dolna krawędź)
R_RULES = [(0.25, 0.85, 0.2, 2, 0, 1, "Rbowl", (0.30, 0.85)),  # dół brzuszka, płynnie wygaszany ku górze
           (0.44, 0.50, 0.2, 0.8, 0, 1, "Rcnt"),              # dół licznika osobno
           (0.30, 1.01, 0.6, 2, 1, 0, "Rright"),              # prawa krawędź brzuszka
           (0.0, 0.01, 0.6, 2, 1, 0, "Rleg")]                 # stopka nogi
G_RULES = [(9, 9, 0, 0, 0, 0, "Gbar"), (0.30, 0.56, 0.3, 1.1, 0, 1, "Gbary")]  # obsługiwane przez g_hook              # lewy koniec poprzeczki G
def build(Wb, Wl):
    r = {"BA": A_rules("bA", Wb["A"], 0.387), "LA": A_rules("lA", Wl["A"], 0.44),
         "BE": E_rules("bE"), "LE": E_rules("lE"), "BR": R_RULES, "LG": G_RULES}
    return r
