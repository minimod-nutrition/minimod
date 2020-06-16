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
$call "gdxxrw input=benefits_zincVAfolate_demwoaz.xlsx output=Cameroon_deathsaverted.gdx index=Indexdeathsaverted!A2"
$gdxin Cameroon_deathsaverted.gdx
$load k j DEATHSAVERTED
option deathsaverted:3:1:1 ;
display k, j, t, deathsaverted ;

* Input LiST results to nutrition interventions
$call "gdxxrw input=benefits_zincVAfolate_demwoaz_high.xlsx output=Cameroon_deathsavertedhigh.gdx index=Indexdeathsavertedhigh!A2"
$gdxin Cameroon_deathsavertedhigh.gdx
$load DEATHSAVERTEDHIGH
option deathsavertedhigh:3:1:1 ;
display deathsavertedhigh ;

* Input cost results to nutrition interventions
$call "gdxxrw input=benefits_zincVAfolate_demwoaz.xlsx output=Cameroon_deathsavertedcost.gdx index=Indexdeathsavertedcost!A2"
$gdxin Cameroon_deathsavertedcost.gdx
$load DEATHSAVERTEDCOST
option deathsavertedcost:3:1:1 ;
display deathsavertedcost ;

* Input cost results to nutrition interventions
$call "gdxxrw input=benefits_zincVAfolate_demwoaz.xlsx output=Cameroon_folate.gdx index=Indexfolate!A2"
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
BETA(t)                  DISCOUNT MULTIPLIER FOR BENEFITS
DISCOUNT2                DISCOUNT FACTOR FOR COSTS
GAMMA(t)                 DISCOUNT MULTIPLIER FOR COSTS
totalfunds               TOTAL FUNDS AVAILABLE
totalbenefits2           TOTAL BENEFITS
totalbenefitsbau         TOTAL BENEFITS OF BAU*
cost(k,j,t)              TOTAL COSTS
cov(k,j,t)               COVERAGE MATRIX
;

* Computing discount rates for costs and benefits (may differ if interest rates differ)
DISCOUNT    = 1/(1+INTLEND);
BETA(t)     = DISCOUNT**(ORD(t)-1) ;
DISCOUNT2    = 1/(1+INTLEND2);
GAMMA(t)     = DISCOUNT2**(ORD(t)-1) ;

* Defining constraint levels
totalfunds = totalfunds1*1;

* Make the coverage and costs parameters
cov(k,j,t)         = deathsaverted(k,j,t) ;
*cov(k,j,t)         = deathsavertedhigh(k,j,t) ;
cost(k,j,t)        = deathsavertedcost(k,j,t) ;

* DEFINE SUBSETSS OF NATIONAL AND SUBNATIONAL INTERVENTIONS
*-------------------------------------------------------------------

set

 cubek(k) /cube,   maxoilcube,
           oilcube, oilcubevas, maxoilcubevas, cubevas, cubeclinic, oilcubeclinic,
           maxoilcubeclinic, cubeflour, maxoilcubeflour, oilcubeflour, oilcubevasflour,
           cubevasflour, maxoilcubevasflour, cliniccubeflour, oilcubeclinicflour,
           maxoilcubeclinicflour, cubeflourzcube, maxoilcubeflourzcube, oilcubeflourzcube, oilcubevasflourzcube,
          cubevasflourzcube, maxoilcubevasflourzcube, cliniccubeflourzcube, oilcubeclinicflourzcube,
           maxoilcubeclinicflourzcube /

 zcubek(k) /zcube, flourzcube, cubezcube, cubeflourzcube, oilvasflourzcube, maxoilcubeflourzcube,
            oilflourzcube, oilclinicflourzcube, oilcubeflourzcube, oilcubevasflourzcube, maxoilvasflourzcube,
            vasflourzcube, clinicflourzcube, cubevasflourzcube, maxoilclinicflourzcube, maxoilcubevasflourzcube,
           cliniccubeflourzcube, oilcubeclinicflourzcube, maxoilcubeclinicflourzcube/

 oilk(k) /oilvas, oil, oilcube, oilcubevas, oilclinic,    oilcubeclinic, oilvasflour, oilflour,
          oilclinicflour, oilcubeflour, oilcubevasflour, oilcubeclinicflour, oilvasflourzcube,
          oilflourzcube,    oilclinicflourzcube, oilcubeflourzcube,  oilcubevasflourzcube, oilcubeclinicflourzcube /

 maxoilk(k) /maxoil, maxoilcube, maxoilvas, maxoilcubevas ,  maxoilclinic, maxoilcubeclinic ,  maxoilflour,
             maxoilcubeflour ,    maxoilvasflour ,    maxoilclinicflour, maxoilcubevasflour  ,    maxoilcubeclinicflour,
             maxoilflourzcube   ,   maxoilcubeflourzcube, maxoilvasflourzcube ,
              maxoilclinicflourzcube    ,    maxoilcubevasflourzcube, maxoilcubeclinicflourzcube /

 flourk(k) /flour, flourzcube,    cubeflour, oilvasflour, maxoilflour, maxoilcubeflour, oilflour,
            oilclinicflour, oilcubeflour, oilcubevasflour ,    maxoilvasflour, vasflour , clinicflour,
            cubevasflour,  maxoilclinicflour, maxoilcubevasflour ,    cliniccubeflour, oilcubeclinicflour ,  maxoilcubeclinicflour,
            cubeflourzcube,   oilvasflourzcube, maxoilflourzcube,    maxoilcubeflourzcube, oilflourzcube, oilclinicflourzcube
            oilcubeflourzcube ,    oilcubevasflourzcube, maxoilvasflourzcube, vasflourzcube, clinicflourzcube, cubevasflourzcube,
            maxoilclinicflourzcube    ,    maxoilcubevasflourzcube, cliniccubeflourzcube      ,    oilcubeclinicflourzcube,
            maxoilcubeclinicflourzcube /

 flouronlyk(k) /flour,  oilvasflour, maxoilflour, oilflour,
            oilclinicflour,     maxoilvasflour, vasflour , clinicflour,
             maxoilclinicflour /

 cubeonlyk(k) /cube,   maxoilcube,
           oilcube, oilcubevas, maxoilcubevas, cubevas, cubeclinic, oilcubeclinic,
           maxoilcubeclinic/

 flourcubek(k) /flourzcube,    cubeflour, maxoilcubeflour,
            oilcubeflour, oilcubevasflour ,
            cubevasflour, maxoilcubevasflour ,    cliniccubeflour, oilcubeclinicflour ,  maxoilcubeclinicflour,
            cubeflourzcube,   oilvasflourzcube, maxoilflourzcube,    maxoilcubeflourzcube, oilflourzcube, oilclinicflourzcube
            oilcubeflourzcube ,    oilcubevasflourzcube, maxoilvasflourzcube, vasflourzcube, clinicflourzcube, cubevasflourzcube,
            maxoilclinicflourzcube    ,    maxoilcubevasflourzcube, cliniccubeflourzcube      ,    oilcubeclinicflourzcube,
            maxoilcubeclinicflourzcube /
;
*Need to adjust all cube benefit interventions because input table has benefits for the first three years
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

display cov ;

*Add Folate benefits
folate("cube",j,t2)=0;
folate("cubeflour",j,t2)=folate("flour",j,t2);
cov(flouronlyk,j,t)=cov(flouronlyk,j,t)+folate("flour",j,t) ;
cov(cubeonlyk,j,t)=cov(cubeonlyk,j,t)+folate("cube",j,t) ;
cov(flourcubek,j,t)=cov(flourcubek,j,t)+folate("cubeflour",j,t) ;


display cov ;


totalbenefitsbau=sum(t,GAMMA(t)*(sum((j),cov("oilvasflour",j,t))));
totalbenefits2=percben*totalbenefitsbau ;

display totalbenefitsbau, totalbenefits2 ;

Variables
X(k,j,t)      QUANTITY OF VA INTERVENTION ZERO OR ONE
XCOST         TOTAL COST FOR X VARIABLE INTERVENTIONS
XCOV          TOTAL COVERAGE FOR X VARIABLE INTERVENTIONS
Z             TOTAL COSTS
BEN           TOTAL COVERAGE
YESCUBE(j,t)   equal to 1 if there is cube in j at t
YESOIL(j,t)    equal to 1 if there is oil in j at t
YESMAXOIL(j,t) equal to 1 if there is oil in j at t
YESZCUBE(j,t)  equal to 1 if there is zinc cube in j at t
YESFLOUR(j,t)  equal to 1 if there is flour in j at t
;

Binary Variable X, Y;

* this is useful to refer to two regions within a single equation
alias (j,jj) ;
alias (t,tt) ;

Equations
benefit                  TOTAL AMOUNT OF COVERAGE BENEFITS
benefitconst             TOTAL AMOUNT OF PEOPLE THAT MUST BENEFIT IN TOTAL

*fundconst                THE TOTAL AMOUNT OF FUNDING
totcost                  TOTAL COSTS FOR THE OPTIMAL INTERVENTIONS
onesx(j,t)               A CONSTRAINT ON THE NUMBER OF INTERVENTIONS THAT CAN BE CHOSEN FOR X VARIABLES INTERVENTIONS
xcoveq(k,j,t)            THE AMOUNT OF COVERAGE FOR X
xcosteq(k,j,t)           THE AMOUNT OF COST FOR X

* Equations that force national interventions to be in all regions:
yescubeeq(j,t)       equation defining yescube>0 if there is cube in j
yeszcubeeq(j,t)       equation defining yeszcube>0 if there is cube in j
yesfloureq(j,t)      equation defining yesflour>0 if there is flour in j
yesoileq(j,t)        equation defining yesoil>0 if there is oil in j
yesmaxoileq(j,t)     equation defining yesmaxoil>0 if there is maxoil in j
allcubeeq(j,jj,t)    equation forcing cube to be either 1 or 0 in all regions
allzcubeeq(j,jj,t)    equation forcing zinc cube to be either 1 or 0 in all regions
allfloureq(j,jj,t)   equation forcing flour to be either 1 or 0 in all regions
alloileq(j,jj,t)     equation forcing oil to be either 1 or 0 in all regions
allmaxoileq(j,jj,t)  equation forcing maxoil to be either 1 or 0 in all regions
alloileq2(j,t,tt)    equation forcing oil to be either 1 or 0 in all time periods
allmaxoileq2(j,t,tt) equation forcing maxoil to be either 1 or 0 in all time periods
allcubeeq2(j,t,tt)   equation forcing cube to be either 1 or 0 in all time periods
allzcubeeq2(j,t,tt)  equation forcing zcube to be either 1 or 0 in all time periods

;


* Coverage and cost:
xcoveq(k,j,t) ..       XCOV(k,j,t)=e=cov(k,j,t)*x(k,j,t);
xcosteq(k,j,t) ..      XCOST(k,j,t)=e=cost(k,j,t)*x(k,j,t);
benefit ..             BEN=e=sum(t,GAMMA(t)*(sum((k,j),XCOV(k,j,t))));
totcost ..             Z=e=sum(t,BETA(t)*(sum((k,j),XCOST(k,j,t)))) ;

* Constraints:
* Equity changes space
*benefitspace(j) ..          BENSPACE(j)=e=sum(t,GAMMA(t)*(sum((k),XCOV(k,j,t)))) ;
*benefitconstspace(j) ..     BENSPACE(j)=g=totalbenefitsbau2(j);

* Equity changes time
*benefittime(t) ..          BENTIME(t)=e=sum(j,GAMMA(t)*(sum((k),XCOV(k,j,t)))) ;
*benefitconsttime(t) ..     BENTIME(t)=g=totalbenefitsbau3(t);

* Equity changes space/time
*benefitspacetime(j,t) ..          BENSPACETIME(j,t)=e=GAMMA(t)*(sum((k),XCOV(k,j,t))) ;
*benefitconstspacetime(j,t) ..     BENSPACETIME(j,t)=g=totalbenefitsbau4(j,t);

benefitconst ..        BEN=g=totalbenefits2;
onesx(j,t)..           sum(k,x(k,j,t))=l=1;


* equations checking if there is flour, oil and cube anywhere:
yescubeeq(j,t)..       yescube(j,t) =e= sum((cubek),x(cubek,j,t)) ;
yeszcubeeq(j,t)..      yeszcube(j,t) =e= sum((zcubek),x(zcubek,j,t)) ;
yesfloureq(j,t)..      yesflour(j,t) =e= sum((flourk),x(flourk,j,t)) ;
yesoileq(j,t)..        yesoil(j,t) =e= sum((oilk),x(oilk,j,t)) ;
yesmaxoileq(j,t)..     yesmaxoil(j,t) =e= sum((maxoilk),x(maxoilk,j,t)) ;

* equations forcing there to be oil or cube everywhere if it is anywhere:
allcubeeq(j,jj,t)..          yescube(j,t) =e= yescube(jj,t) ;
allzcubeeq(j,jj,t)..         yeszcube(j,t) =e= yeszcube(jj,t) ;
alloileq(j,jj,t)..           yesoil(j,t) =e= yesoil(jj,t) ;
allmaxoileq(j,jj,t)..        yesmaxoil(j,t) =e= yesmaxoil(jj,t) ;
allfloureq(j,jj,t)..         yesflour(j,t) =e= yesflour(jj,t) ;

* equations forcing there to be cube, in all times if it at anytime:
alloileq2(j,t2,tt)..         yesoil(j,tt) =e=yesoil(j,t2) ;
allmaxoileq2(j,t2,tt)..      yesmaxoil(j,tt) =e=yesmaxoil(j,t2) ;
allcubeeq2(j,t2,tt)..        yescube(j,tt) =e=yescube(j,t2) ;
allzcubeeq2(j,t2,tt)..       yeszcube(j,tt) =e=yeszcube(j,t2) ;

Model nutrition /all/ ;
option minlp=BONMIN ;
Solve nutrition using minlp minimizing z ;
Display  x.l,  z.l, ben.l, xcov.l, xcost.l, totalfunds, totalbenefits;

Parameters
finalcov         Coverage per time period all
finalcost        Cost per time period
finalcovspace    Coverage per time period all
finalcostspace   Cost per time period
covbau           Coverage per time for BAU scenario
costbau          Cost per time for BAU scenario
covbauspace      Coverage per space for BAU scenario
costbauspace     Cost per space for BAU scenario
tfinalcov        Total coverage for optimal model
tfinalcost       Total costs for optimal model
tcovbau          Total coverage for BAU
tcostbau         Total cost for BAU
tcovbauspace     Total coverage per space for BAU scenario
tcostbauspace    Total cost per space for BAU scenario
costpc           Cost per child 6-59 months
costbaupc        Cost per child 6-59 months for BAU scenario
;
finalcov(t)              =sum(k,sum(j,xcov.l(k,j,t)))  ;
finalcost(t)             =sum(k,sum(j,xcost.l(k,j,t))) ;
covbau(t)                =sum(j,cov("oilvasflour",j,t))  ;
costbau(t)               =sum(j,cost("oilvasflour",j,t))  ;
covbauspace(j)           =sum(t,cov("oilvasflour",j,t))  ;
costbauspace(j)          =sum(t,cost("oilvasflour",j,t))  ;
costbaupc                =sum(t,costbau(t))/sum(t,covbau(t));
finalcovspace(j)         =sum(k,sum(t,xcov.l(k,j,t)))  ;
finalcostspace(j)        =sum(k,sum(t,xcost.l(k,j,t))) ;
tfinalcov                =sum(t,finalcov(t));
tfinalcost               =sum(t,finalcost(t));
tcovbau                  =sum(t,covbau(t));
tcostbau                 =sum(t,costbau(t));
tcovbauspace             =sum(j,covbauspace(j));
tcostbauspace            =sum(j,costbauspace(j));
tcovbau                  =sum(t,covbau(t));
tcostbau                 =sum(t,costbau(t));
costpc                   =sum(t,finalcost(t))/sum(t,finalcov(t)) ;

display finalcov, finalcost, covbau, costbau, covbauspace, costbauspace, costbaupc, costpc, tcovbau, tcostbau, tcovbauspace, tcostbauspace,
finalcovspace, finalcostspace;

* #################################################################################################
* ################################# OUTPUT THE TABLE WITH A PUT STATEMENT #########################
* #################################################################################################
* (This is useful to automate certain kinds of output and avoid repetitive excel manipulations
* It makes a text file (table1.txt) which can be easily cut and pasted into excel.

* OUTPUT: after the run, open the following .txt file.
* It can be cut+pasted to excel for easy comparison between runs
* (do a text-to-columns with semicolon as the separator)
file tablput20_4bk /table1.txt/;
put tablput20_4bk ;

* This is to have capital values in the denominator of the multipliers
put 'OPTIMIZED SCENARIO' /;

put 'Total cost and coverage by year' /;
loop(t,
     put t.tl 'cost';
     put  @45';' finalcost(t):12:0 /;
);
loop(t,
     put t.tl 'coverage';
     put  @45';' finalcov(t):12:0 /;
);
put //;

put 'Total cost and coverage by year for bau*' /;
loop(t,
     put t.tl 'cost';
     put  @45';' costbau(t):12:0 /;
);
loop(t,
     put t.tl 'coverage';
     put  @45';' covbau(t):12:0 /;
);
put //;

put 'Discounted total cost for BAU'/;
         put @45';' tcostbau:12:0 /;

put 'Discounted total benefits for BAU'/;
         put @45';' tcovbau:12:0 /;

put 'Discounted cost per child 6-59 months for BAU'/;
         put @45';' costbaupc:6:2 /;

put 'Discounted total cost for optimal simulation'/;
         put @45';' tfinalcost:12:0 /;

put 'Discounted total benefits for optimal simulation'/;
         put @45';' tfinalcov:12:0 /;

put 'Discounted cost per child 6-59 months for optimal simulation'/;
         put @45';' costpc:6:2 /;
