$TITLE CAMEROON COVERAGE MODEL
* Justin Kagin, June 2014

* The model reads in data from excel spreadsheet in the form of parameter distributions
* Then it uses them to make a coverage model for Cameroon

* A few useful gams options
option limrow=30 ;
option limcol=30 ;



$offlisting ;
Sets
k interventions
j space
t time /1*10/
;
set t2(t) just the first 3 years /1, 2, 3 /
    ts(t) /1,2,3,4/
    t3(t) years 4 to 10 /4,5,6,7,8,9,10/
    t4(t) just the first 2 years /1,2/
* choose the number of draws (ex: change the second number from dr11 to dr499)
* nb: must be greater than 10 to allow for percentiles to be computed
    draw /dr0*dr9/ ;


parameter
deathsavertedcost(k,j,t)   Deaths Averted for VA and Zinc
deathsaverted(k,j,t)       Deaths Averted for VA and Zinc
deathsavertedhigh(k,j,t)   Deaths Averted for VA and Zinc with high VA
folate(k,j,t)              Deaths Averted for Folate
;
* 1) Read in the data from all spreadsheets:
*--------------------------------------------------------------------------

* As a general rule, you should use one gdx file for each spreadsheet (keeps things clean)

* Input LiST results to nutrition interventions
*$call "gdxxrw input=benefits_zincVAfolate_demwoaz.xlsx output=Cameroon_deathsaverted.gdx index=Indexdeathsaverted!A2"
$gdxin Cameroon_deathsaverted.gdx
$load k j DEATHSAVERTED
option deathsaverted:3:1:1 ;
display k, j, t, deathsaverted ;

* Input LiST results to nutrition interventions
*$call "gdxxrw input=benefits_zincVAfolate_demwoaz_high.xlsx output=Cameroon_deathsavertedhigh.gdx index=Indexdeathsavertedhigh!A2"
$gdxin Cameroon_deathsavertedhigh.gdx
$load DEATHSAVERTEDHIGH
option deathsavertedhigh:3:1:1 ;
display deathsavertedhigh ;

* Input cost results to nutrition interventions
*$call "gdxxrw input=benefits_zincVAfolate_demwoaz.xlsx output=Cameroon_deathsavertedcost.gdx index=Indexdeathsavertedcost!A2"
$gdxin Cameroon_deathsavertedcost.gdx
$load DEATHSAVERTEDCOST
option deathsavertedcost:3:1:1 ;
display deathsavertedcost ;

* Input cost results to nutrition interventions
*$call "gdxxrw input=benefits_zincVAfolate_demwoaz.xlsx output=Cameroon_folate.gdx index=Indexfolate!A2"
$gdxin Cameroon_folate.gdx
$load FOLATE
option folate:3:1:1 ;
display folate ;



Scalar
totalfunds1 total funds available /35821703/
totalbenefits total benefits available /13458058/
s loop value /1/
percben      Percentage of bau* benefits                 /1/
INTLEND      INTEREST RATE ON FUNDS LOANED OUT           /0/
INTLEND2     INTEREST RATE ON BENEFITS                  /0.03/;


Parameter
DISCOUNT                 DISCOUNT FACTOR FOR BENEFITS
BETA(ts)                  DISCOUNT MULTIPLIER FOR BENEFITS
DISCOUNT2                DISCOUNT FACTOR FOR COSTS
GAMMA(ts)                 DISCOUNT MULTIPLIER FOR COSTS
totalfunds               TOTAL FUNDS AVAILABLE
totalbenefits2           TOTAL BENEFITS
totalbenefitsbau         TOTAL BENEFITS OF BAU*
cost(k,j,t)              TOTAL COSTS
cov(k,j,t)               COVERAGE MATRIX

;

* Computing discount rates for costs and benefits (may differ if interest rates differ)
DISCOUNT    = 1/(1+INTLEND);
BETA(ts)     = DISCOUNT**(ORD(ts)-1) ;
DISCOUNT2    = 1/(1+INTLEND2);
GAMMA(ts)     = DISCOUNT2**(ORD(ts)-1) ;

* Defining constraint levels
totalfunds = totalfunds1*1;

* Make the coverage and costs parameters
cov(k,j,t)         = deathsaverted(k,j,t) ;
*cov(k,j,t)         = deathsavertedhigh(k,j,t) ;
cost(k,j,t)        = deathsavertedcost(k,j,t) ;


cov("cube",j,t2)=0                              ;
cov("cubezcube",j,t2)=0                         ;
cov("maxoilcube",j,t2)=cov("maxoil",j,t2) ;
cov("oilcube",j,t2)=cov("oil",j,t2)       ;
cov("oilcubevas",j,t2)=cov("oilvas",j,t2) ;
cov("maxoilcubevas",j,t2)=cov("maxoilvas",j,t2) ;
cov("cubevas",j,t2)=cov("vas",j,t2) ;
cov("cubeclinic",j,t2)=cov("clinic",j,t2) ;
cov("maxoilcubeclinic",j,t2)=cov("maxoilclinic",j,t2) ;
cov("oilcubeclinic",j,t2)=cov("oilclinic",j,t2) ;
cov("cubeflour",j,t2)=cov("flour",j,t2) ;
cov("maxoilcubeflour",j,t2)=cov("maxoilflour",j,t2) ;
cov("oilcubeflour",j,t2)=cov("oilflour",j,t2) ;
cov("oilcubevasflour",j,t2)=cov("oilvasflour",j,t2) ;
cov("cubevasflour",j,t2)=cov("vasflour",j,t2) ;
cov("maxoilcubevasflour",j,t2)=cov("maxoilvasflour",j,t2) ;
cov("cliniccubeflour",j,t2)=cov("clinicflour",j,t2) ;
cov("oilcubeclinicflour",j,t2)=cov("oilclinicflour",j,t2) ;
cov("maxoilcubeclinicflour",j,t2)=cov("maxoilclinicflour",j,t2) ;
cov("cubeflourzcube",j,t2)=cov("flour",j,t2) ;
cov("maxoilcubeflourzcube",j,t2)=cov("maxoilflour",j,t2) ;
cov("oilcubeflourzcube",j,t2)=cov("oilflour",j,t2) ;
cov("oilcubevasflourzcube",j,t2)=cov("oilvasflour",j,t2) ;
cov("cliniccubeflourzcube",j,t2)=cov("clinicflour",j,t2) ;
cov("oilcubeclinicflourzcube",j,t2)=cov("oilclinicflour",j,t2) ;
cov("maxoilcubeclinicflourzcube",j,t2)=cov("maxoilclinicflour",j,t2) ;

cov("zcube",j,t2)=0                      ;
cov("flourzcube",j,t2)=cov("flour",j,t2) ;
cov("oilvasflourzcube",j,t2)=cov("oilvasflour",j,t2) ;
cov("maxoilcubeflourzcube",j,t2)=cov("maxoilflour",j,t2) ;
cov("oilflourzcube",j,t2)=cov("oilflour",j,t2) ;

*Need to adjust all oil benefit interventions because input table has benefits for the first two years at 75% of target
cov("maxoil",j,t4)=cov("oil",j,t4) ;
cov("maxoilcube",j,t4)=cov("oilcube",j,t4) ;
cov("maxoilvas",j,t4)=cov("oilvas",j,t4) ;
cov("maxoilcubevas",j,t4)=cov("oilcubevas",j,t4) ;
cov("maxoilclinic",j,t4)=cov("oilclinic",j,t4) ;
cov("maxoilcubeclinic",j,t4)=cov("oilcubeclinic",j,t4) ;
cov("maxoilflour",j,t4)=cov("oilflour",j,t4) ;
cov("maxoilcubeflour",j,t4)=cov("oilcubeflour",j,t4) ;
cov("maxoilvasflour",j,t4)=cov("oilvasflour",j,t4) ;
cov("maxoilclinicflour",j,t4)=cov("oilclinicflour",j,t4) ;
cov("maxoilcubevasflour",j,t4)=cov("oilcubevasflour",j,t4) ;
cov("maxoilcubeclinicflour",j,t4)=cov("oilcubeclinicflour",j,t4) ;
cov("maxoilflourzcube",j,t4)=cov("oilflourzcube",j,t4) ;
cov("maxoilcubeflourzcube",j,t4)=cov("oilcubeflourzcube",j,t4) ;
cov("maxoilvasflourzcube",j,t4)=cov("oilvasflourzcube",j,t4) ;
cov("maxoilclinicflourzcube",j,t4)=cov("oilclinicflourzcube",j,t4) ;
cov("maxoilcubevasflourzcube",j,t4)=cov("oilcubevasflourzcube",j,t4) ;
cov("maxoilcubeclinicflourzcube",j,t4)=cov("oilcubeclinicflourzcube",j,t4) ;




* DEFINE SUBSETSS OF NATIONAL AND SUBNATIONAL INTERVENTIONS
*-------------------------------------------------------------------

Singleton Set

 cubek(k) /cube /

 zcubek(k) /zcube/

 oilk(k) /oil/

 maxoilk(k) /maxoil/

 flourk(k) /flour /;
 
Set
            
sub(k) /cube, zcube, oil, maxoil, flour, oilvasflour/
;

cov("cube",j,t2)=0                              ;
cov("cubezcube",j,t2)=0                         ;
cov("maxoilcube",j,t2)=cov("maxoil",j,t2) ;
cov("oilcube",j,t2)=cov("oil",j,t2)       ;
cov("oilcubevas",j,t2)=cov("oilvas",j,t2) ;
cov("maxoilcubevas",j,t2)=cov("maxoilvas",j,t2) ;
cov("cubevas",j,t2)=cov("vas",j,t2) ;
cov("cubeclinic",j,t2)=cov("clinic",j,t2) ;
cov("maxoilcubeclinic",j,t2)=cov("maxoilclinic",j,t2) ;
cov("oilcubeclinic",j,t2)=cov("oilclinic",j,t2) ;
cov("cubeflour",j,t2)=cov("flour",j,t2) ;
cov("maxoilcubeflour",j,t2)=cov("maxoilflour",j,t2) ;
cov("oilcubeflour",j,t2)=cov("oilflour",j,t2) ;
cov("oilcubevasflour",j,t2)=cov("oilvasflour",j,t2) ;
cov("cubevasflour",j,t2)=cov("vasflour",j,t2) ;
cov("maxoilcubevasflour",j,t2)=cov("maxoilvasflour",j,t2) ;
cov("cliniccubeflour",j,t2)=cov("clinicflour",j,t2) ;
cov("oilcubeclinicflour",j,t2)=cov("oilclinicflour",j,t2) ;
cov("maxoilcubeclinicflour",j,t2)=cov("maxoilclinicflour",j,t2) ;
cov("cubeflourzcube",j,t2)=cov("flour",j,t2) ;
cov("maxoilcubeflourzcube",j,t2)=cov("maxoilflour",j,t2) ;
cov("oilcubeflourzcube",j,t2)=cov("oilflour",j,t2) ;
cov("oilcubevasflourzcube",j,t2)=cov("oilvasflour",j,t2) ;
cov("cliniccubeflourzcube",j,t2)=cov("clinicflour",j,t2) ;
cov("oilcubeclinicflourzcube",j,t2)=cov("oilclinicflour",j,t2) ;
cov("maxoilcubeclinicflourzcube",j,t2)=cov("maxoilclinicflour",j,t2) ;

cov("zcube",j,t2)=0                      ;
cov("flourzcube",j,t2)=cov("flour",j,t2) ;
cov("oilvasflourzcube",j,t2)=cov("oilvasflour",j,t2) ;
cov("maxoilcubeflourzcube",j,t2)=cov("maxoilflour",j,t2) ;
cov("oilflourzcube",j,t2)=cov("oilflour",j,t2) ;

*Need to adjust all oil benefit interventions because input table has benefits for the first two years at 75% of target
cov("maxoil",j,t4)=cov("oil",j,t4) ;
cov("maxoilcube",j,t4)=cov("oilcube",j,t4) ;
cov("maxoilvas",j,t4)=cov("oilvas",j,t4) ;
cov("maxoilcubevas",j,t4)=cov("oilcubevas",j,t4) ;
cov("maxoilclinic",j,t4)=cov("oilclinic",j,t4) ;
cov("maxoilcubeclinic",j,t4)=cov("oilcubeclinic",j,t4) ;
cov("maxoilflour",j,t4)=cov("oilflour",j,t4) ;
cov("maxoilcubeflour",j,t4)=cov("oilcubeflour",j,t4) ;
cov("maxoilvasflour",j,t4)=cov("oilvasflour",j,t4) ;
cov("maxoilclinicflour",j,t4)=cov("oilclinicflour",j,t4) ;
cov("maxoilcubevasflour",j,t4)=cov("oilcubevasflour",j,t4) ;
cov("maxoilcubeclinicflour",j,t4)=cov("oilcubeclinicflour",j,t4) ;
cov("maxoilflourzcube",j,t4)=cov("oilflourzcube",j,t4) ;
cov("maxoilcubeflourzcube",j,t4)=cov("oilcubeflourzcube",j,t4) ;
cov("maxoilvasflourzcube",j,t4)=cov("oilvasflourzcube",j,t4) ;
cov("maxoilclinicflourzcube",j,t4)=cov("oilclinicflourzcube",j,t4) ;
cov("maxoilcubevasflourzcube",j,t4)=cov("oilcubevasflourzcube",j,t4) ;
cov("maxoilcubeclinicflourzcube",j,t4)=cov("oilcubeclinicflourzcube",j,t4) ;
*Need to adjust all cube benefit interventions because input table has benefits for the first three years
Parameter
newcost(sub,j,ts)
newcov(sub,j,ts);

newcov(sub, j, ts) = cov(sub,j,ts);
newcost(sub, j, ts) = cost(sub,j,ts);

display newcov;
display newcost;



totalbenefitsbau=sum(ts, GAMMA(ts)*(sum((j),newcov("oilvasflour",j,ts))));
totalbenefits2=percben*totalbenefitsbau ;

display totalbenefitsbau, totalbenefits2 ;

Variables
X(sub,j,ts)      QUANTITY OF VA INTERVENTION ZERO OR ONE
XCOST         TOTAL COST FOR X VARIABLE INTERVENTIONS
XCOV          TOTAL COVERAGE FOR X VARIABLE INTERVENTIONS
Z             TOTAL COSTS
BEN           TOTAL COVERAGE
YESCUBE(j,ts)   equal to 1 if there is cube in j at t
YESOIL(j,ts)    equal to 1 if there is oil in j at t
YESMAXOIL(j,ts) equal to 1 if there is oil in j at t
YESZCUBE(j,ts)  equal to 1 if there is zinc cube in j at t
YESFLOUR(j,ts)  equal to 1 if there is flour in j at t
;

Binary Variable X;

* this is useful to refer to two regions within a single equation
alias (j,jj) ;
alias (ts,tt) ;

Equations
benefit                  TOTAL AMOUNT OF COVERAGE BENEFITS
benefitconst             TOTAL AMOUNT OF PEOPLE THAT MUST BENEFIT IN TOTAL

*fundconst                THE TOTAL AMOUNT OF FUNDING
totcost                  TOTAL COSTS FOR THE OPTIMAL INTERVENTIONS
onesx(j,ts)               A CONSTRAINT ON THE NUMBER OF INTERVENTIONS THAT CAN BE CHOSEN FOR X VARIABLES INTERVENTIONS
xcoveq(sub,j,ts)            THE AMOUNT OF COVERAGE FOR X
xcosteq(sub,j,ts)           THE AMOUNT OF COST FOR X

* Equations that force national interventions to be in all regions:
yescubeeq(j,ts)       equation defining yescube>0 if there is cube in j
yeszcubeeq(j,ts)       equation defining yeszcube>0 if there is cube in j
yesfloureq(j,ts)      equation defining yesflour>0 if there is flour in j
yesoileq(j,ts)        equation defining yesoil>0 if there is oil in j
yesmaxoileq(j,ts)     equation defining yesmaxoil>0 if there is maxoil in j
allcubeeq(j,jj,ts)    equation forcing cube to be either 1 or 0 in all regions
allzcubeeq(j,jj,ts)    equation forcing zinc cube to be either 1 or 0 in all regions
allfloureq(j,jj,ts)   equation forcing flour to be either 1 or 0 in all regions
alloileq(j,jj,ts)     equation forcing oil to be either 1 or 0 in all regions
allmaxoileq(j,jj,ts)  equation forcing maxoil to be either 1 or 0 in all regions
*alloileq2(j,ts,tt)    equation forcing oil to be either 1 or 0 in all time periods
*allmaxoileq2(j,ts,tt) equation forcing maxoil to be either 1 or 0 in all time periods
*allcubeeq2(j,ts,tt)   equation forcing cube to be either 1 or 0 in all time periods
*allzcubeeq2(j,ts,tt)  equation forcing zcube to be either 1 or 0 in all time periods

;


* Coverage and cost:
xcoveq(sub,j,ts) ..       XCOV(sub,j,ts)=e=newcov(sub,j,ts)*x(sub,j,ts);
xcosteq(sub,j,ts) ..      XCOST(sub,j,ts)=e=newcost(sub,j,ts)*x(sub,j,ts);
benefit ..             BEN=e=sum(ts,GAMMA(ts)*(sum((sub,j),XCOV(sub,j,ts))));
totcost ..             Z=e=sum(ts,BETA(ts)*(sum((sub,j),XCOST(sub,j,ts)))) ;

benefitconst ..        BEN=g=totalbenefits2;
onesx(j,ts)..           sum(sub,x(sub,j,ts))=l=1;



* equations checking if there is flour, oil and cube anywhere:
yescubeeq(j,ts)..       yescube(j,ts) =e= x("cube",j,ts) ;
yeszcubeeq(j,ts)..      yeszcube(j,ts) =e= x("zcube",j,ts) ;
yesfloureq(j,ts)..      yesflour(j,ts) =e= x("flour",j,ts) ;
yesoileq(j,ts)..        yesoil(j,ts) =e= x("oil",j,ts) ;
yesmaxoileq(j,ts)..     yesmaxoil(j,ts) =e= x("maxoil",j,ts) ;

* equations forcing there to be oil or cube everywhere if it is anywhere:
allcubeeq(j,jj,ts)..          yescube(j,ts) =e= yescube(jj,ts) ;
allzcubeeq(j,jj,ts)..         yeszcube(j,ts) =e= yeszcube(jj,ts) ;
alloileq(j,jj,ts)..           yesoil(j,ts) =e= yesoil(jj,ts) ;
allmaxoileq(j,jj,ts)..        yesmaxoil(j,ts) =e= yesmaxoil(jj,ts) ;
allfloureq(j,jj,ts)..         yesflour(j,ts) =e= yesflour(jj,ts) ;

** equations forcing there to be cube, in all times if it at anytime:
*alloileq2(j,t2,ts)..         yesoil(j,ts) =e=yesoil(j,t2) ;
*allmaxoileq2(j,t2,ts)..      yesmaxoil(j,ts) =e=yesmaxoil(j,t2) ;
*allcubeeq2(j,t2,ts)..        yescube(j,ts) =e=yescube(j,t2) ;
*allzcubeeq2(j,t2,ts)..       yeszcube(j,ts) =e=yeszcube(j,t2)  ;


Model nutrition /all/ ;
option minlp=BONMIN ;
Solve nutrition using minlp minimizing z ;
Display  x.l, z.l, ben.l, xcov.l, xcost.l, totalfunds, totalbenefits;




