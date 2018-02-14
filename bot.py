import pywikibot

PAGENAME = "Εξεταστική Χειμερινή 2018"

# before running the bot, you should login `python pwb.py login` with the bot credentials in the shmmywiki site

with open("outputs/export_wiki.txt", "r", encoding="utf8") as f:
	site = pywikibot.Site()
	# fetch the corresponding page of the course
	page = pywikibot.Page(site, PAGENAME)
	body = '{| class="sortable wikitable" style="text-align:left"' + "\n"
	body += '! Μάθημα !! Εξ. !! Ροή !! Εξέταση !! Αποτελέσματα !! Διαφορά !! class="unsortable"|Σύνδεσμος' + "\n"
	body += '|-' + "\n"
	body += f.read()
	body += "\n"
	body += '|}' + "\n"
	body += '----' + "\n"
	body += 'Disclaimer: Η παρούσα σελίδα παράγεται αυτόματα και είναι ακόμη σε δοκιμαστικό στάδιο, επομένως είναι πολύ πιθανό να περιέχει λανθασμένες πληροφορίες. Τα δεδομένα λαμβάνονται από το αντίστοιχο τόπικ αποτελεσμάτων.' + "\n"
	body += '[[Κατηγορία:Εξεταστική]]'
	page.text = body
	page.save(u"Update αποτελεσμάτων [Αυτόματη επεξεργασία από ShmmywikiBot (χειριστής Tdiam)]")
