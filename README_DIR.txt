file README_DIR.txt    descrive il contenuto della directory

progetto django servizi + django-spese (app)

ambiente costruito con virtualenv (python 3.5.1)
+ django 1.9
+ django-taggit 0.20.2
+ pytz 2016.6.1

le directory sono come segue:

* progetto_servizi   directory di base
**  env                ambiente virtualenv
**  etc                una copia delle configurazioni specifiche
                         di apache in centos 6 per questo progetto
                         (deployment)
**  django-spese       build del rilascio della app django-spese
***   spese              app django-spese, copia in rilascio
***   build              directory per l'archivio di rilascio e per le
                           attività relative
***   docs               documentazione della app
**  servizi            progetto django (sviluppo), contenitore di base
***   servizi            progetto django vero e proprio
***   spese              app django-spese in sviluppo
***   static             file statici di progetto
***   templates          templates di progetto
***   expense            NON CONSIDERARE dir.della app django-expense
                           ho usato (semplificando) i suoi models come
                           seed iniziale
**  zarchivio          archivio di codice e utility sperimentate nel
                         corso del progetto, codice obsoleto