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
livessavedcosts(k,j,t)   Deaths Averted for VA and Zinc
livessaved(k,j,t)       Deaths Averted for VA and Zinc
livessavedhigh(k,j,t)   Deaths Averted for VA and Zinc with high VA
;
* 1) Read in the data from all spreadsheets:
*--------------------------------------------------------------------------

* As a general rule, you should use one gdx file for each spreadsheet (keeps things clean)

* Input LiST results to nutrition interventions
$call "gdxxrw input=lives_saved_costs.xlsx output=Cameroon_livessaved.gdx index=Indexlivessaved!A2"
$gdxin Cameroon_livessaved.gdx
$load k j LIVESSAVED
option livessaved:3:1:1 ;
display k, j, t, livessaved ;

* Input LiST results to nutrition interventions
$call "gdxxrw input=lives_saved_costs.xlsx output=Cameroon_livessavedhigh.gdx index=Indexlivessavedhigh!A2"
$gdxin Cameroon_livessavedhigh.gdx
$load LIVESSAVEDHIGH
option livessavedhigh:3:1:1 ;
display livessavedhigh ;

* Input cost results to nutrition interventions
$call "gdxxrw input=lives_saved_costs.xlsx output=Cameroon_livessavedcosts.gdx index=Indexlivessavedcosts!A2"
$gdxin Cameroon_livessavedcosts.gdx
$load LIVESSAVEDCOSTS
option livessavedcosts:3:1:1 ;
display livessavedcosts ;


Scalar
totalfunds1 total funds available /35821703/
totalbenefits total benefits available /13458058/
s loop value /1/
percben      Percentage of bau* benefits                 /1./
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
totalcostsbau            TOTAL COSTS OF BAU*
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
*cov(k,j,t)         = livessaved(k,j,t) ;
cov(k,j,t)         = livessavedhigh(k,j,t) ;
cost(k,j,t)        = livessavedcosts(k,j,t) ;

* DEFINE SUBSETSS OF NATIONAL AND SUBNATIONAL INTERVENTIONS
*-------------------------------------------------------------------

set

 cubek(k) /cube,   maxoilcube, cubezflourfflour,  cubefcube, cubezcubefcube, maxoilcubefcube,  oilcubefflour,
           oilcube, oilcubevas, maxoilcubevas, cubevas, cubeclinic, oilcubeclinic, cubezflourfcube, maxoilcubezflourfcubefflour
           maxoilcubeclinic, cubezflour, maxoilcubezflour, oilcubezflour, oilcubevaszflour, oilcubefcube, maxoilcubezflourzcubefcube
           cubevaszflour, maxoilcubevaszflour, cubefcubefflour, cubezcubefcubefflour, cubecliniczflourzcubefcubefflour
          cubezflourzcube, maxoilcubezflourzcube, oilcubezflourzcube, oilcubevaszflourzcube,   cubecliniczflourfcubefflour
          cubevaszflourzcube, maxoilcubevaszflourzcube,  maxoilcubezflourfflour, cubecliniczflourzcubefcube, cubevaszflourzcubefcube
           oilcubezflourfflour, cubezflourzcubefflour, cubecliniczflourzcubefflour, cubecliniczflourfcube, cubevaszflourzcubefcubefflour
           maxoilcubefflour, cubeclinicfcube, maxoilcubezflourzcubefcubefflour, oilcubezflourfcubefflour, maxoilcubezflourfcube,
           cubevasfcube, maxoilcubefcubefflour, cubecliniczflourfflour, cubevaszflourfcube, cubevaszflourfcubefflour, oilcubefcubefflour,
           cubezflourfcubefflour, cubevaszflourzcubefflour, cubevasfcubefflour, cubezflourzcubefcubefflour, oilcubezflourzcubefcubefflour,
           oilcubezflourfcube, maxoilcubecliniczflourfflour, oilcubecliniczflourfcubefflour, oilcubecliniczflourzcubefcubefflour,
           maxoilcubecliniczflourzcubefcube, maxoilcubeclinicfcube, oilcubecliniczflourfflour, maxoilcubecliniczflourfcubefflour,
           maxoilcubecliniczflourzcubefflour, maxoilcubeclinicfcubefflour, oilcubeclinicfcube, oilcubecliniczflourfcube, oilcubeclinicfcubefflour   /

 zcubek(k) /zcube, zflourzcube, cubezcube, cubezflourzcube, oilvaszflourzcube, maxoilcubezflourzcube, zcubefcube
            oilzflourzcube, oilcubezflourzcube, oilcubevaszflourzcube, maxoilzflourzcube, maxoilvaszflourzcube, zflourzcubefcube
            vaszflourzcube, cubevaszflourzcube, maxoilcubevaszflourzcube, zflourzcubefcubefflour, oilcubezflourzcubefcube, maxoilzflourzcubefcube
            oilzflourzcubefflour, cubezcubefcube, maxoilcubecliniczflourfcube, oilzflourzcubefcubefflour, oilcubecliniczflourzcubefcube /

 fcubek(k) /fcube, oilfcube, cubezflourzcubefcubefflour, cubezflourzcubefcube, cubezflourfcubefflour, maxoilfcube, maxoilcubezflourfcube, maxoilfcubefflour,
            maxoilzflourzcubefcube, oilzflourfcubefflour, oilzflourfcube, maxoilzflourzcubefcubefflour, maxoilcliniczflourfcubefflour,
           oilcubezflourzcubefcube, oilfcubefflour, cubefcubefflour, maxoilzflourfcubefflour, maxoilcubecliniczflourzcubefcubefflour, oilcubezflourfcubefflour,
           maxoilcubeclinicfcube, maxoilcubecliniczflourzcubefcube, cubefcube, oilcubefcube, oilcubeclinicfcube, oilcubecliniczflourfcube,
           oilcubecliniczflourzcubefcube, oilvasfcubefflour    /

 oilk(k) /oilvas, oil, oilcube, oilcubevas, oilclinic,    oilcubeclinic, oilvaszflour, oilzflour, oilzflourfflour, oilcubecliniczflourfflour, oilcubezflourzcubefflour
          oilcliniczflour, oilcubezflour, oilcubevaszflour, oilcubecliniczflour, oilvaszflourzcube, oilfcube, oilcubezflourzcubefcube, oilcubezflourfcube, oilcubezflourfcubefflour
          oilzflourzcube,    oilcliniczflourzcube, oilcubezflourzcube,  oilcubevaszflourzcube, oilcubecliniczflourzcube, oilcubezflourzcubefcubefflour
          oilcubefcubefflour, oilzflourfcubefflour, oilcubecliniczflourzcubefcubefflour, oilcubeclinicfcube,  oilzflourzcubefcubefflour, oilcubecliniczflourzcubefcube,
          oilzflourzcubefcube, oilcubecliniczflourfcube, oilcubecliniczflourfcubefflour, oilcubecliniczflourzcubefflour, oilzflourfcube, oilfcubefflour
          oilcubeclinicfcubefflour, oilcliniczflourfcubefflour, oilcubevaszflourzcubefcubefflour, oilcubeclinicfflour, oilzflourzcubefflour, oilcubevasfcube,
          oilcubevaszflourzcubefcube, oilvaszflourfcubefflour, oilcubevaszflourfcube, oilcliniczflourzcubefcube, oilvasfcubefflour, oilcubevaszflourfcubefflour,
          oilcliniczflourfflour, oilcubevaszflourzcubefflour, oilcubefcube, oilcubezflourfflour, oilcubefflour    /

 maxoilk(k) /maxoil, maxoilcube, maxoilvas, maxoilcubevas ,  maxoilclinic, maxoilcubeclinic ,  maxoilzflour, maxoilcubezflourzcubefcube, maxoilzflourfcubefflour
             maxoilcubezflour ,    maxoilvaszflour ,    maxoilcliniczflour, maxoilcubevaszflour  ,    maxoilcubecliniczflour, maxoilcubefcubefflour, maxoilcubefcube
             maxoilzflourzcube   ,   maxoilcubezflourzcube, maxoilvaszflourzcube ,   maxoilcubezflourzcubefcubefflour, maxoilcubezflourfcubefflour
              maxoilcliniczflourzcube    ,    maxoilcubevaszflourzcube, maxoilcubecliniczflourzcube, maxoilcubezflourfcube, maxoilcubecliniczflourzcubefcubefflour,
            maxoilcubezflourzcubefflour, maxoilcubecliniczflourzcubefcube, maxoilcubeclinicfcube, maxoilzflourzcubefcubefflour, maxoilzflourzcubefcube,
            maxoilcubecliniczflourfcubefflour, maxoilzflourfflour, maxoilcubecliniczflourfcube, maxoilzflourfcube, maxoilcubecliniczflourzcubefflour, maxoilzflourzcubefflour
            maxoilfcubefflour, maxoilcubeclinicfcubefflour, maxoilcliniczflourfcubefflour, maxoilcubeclinicfflour, maxoilfcube, maxoilcubevaszflourzcubefcubefflour,
           maxoilcubevaszflourzcubefcube, maxoilcliniczflourzcubefcube, maxoilcliniczflourzcubefcubefflour, maxoilcubevasfcube, maxoilcubecliniczflourfflour,
           maxoilcubezflourfflour, maxoilcubefflour /

 zflourk(k) /zflour, zflourzcube,    cubezflour, oilvaszflour, maxoilzflour, maxoilcubezflour, oilzflour,  zflourfcube , zflourzcubefcubefflour, cubezflourfcube
            oilcliniczflour, oilcubezflour, oilcubevaszflour, vaszflour , cliniczflour, cliniczflourfflour, oilzflourfflour
            cubevaszflour,  maxoilcliniczflour, maxoilcubevaszflour , oilcubecliniczflourfflour, zflourfflour,  oilzflourfcubefflour, oilzflourfcube
            cubezflourzcube,   oilvaszflourzcube, maxoilzflourzcube,    maxoilcubezflourzcube, oilzflourzcube,  maxoilcubecliniczflourfflour, maxoilzflourfcubefflour
            oilcubezflourzcube ,    oilcubevaszflourzcube, maxoilvaszflourzcube, vaszflourzcube,  cubevaszflourzcube    ,    maxoilcubevaszflourzcube,
           maxoilzflourfflour, oilzflourzcubefcubefflour, zflourfcubefflour, zflourzcubefflour, maxoilzflourfcube, oilzflourzcubefcube, oilcliniczflourfcubefflour
            oilcubezflourzcubefcubefflour, oilcubezflourzcubefcube, oilcliniczflourfflour, cubezflourzcubefflour, maxoilcliniczflourfcubefflour, maxoilvaszflour,
           oilcubecliniczflourzcubefcubefflour, cubezflourfflour, cubezflourzcubefcubefflour, oilcubezflourfcube, oilcubezflourfflour, cubezflourfcubefflour,
           oilcubecliniczflourzcubefcube, maxoilzflourzcubefcube  /

 fflourk(k) /fflour, oilzflourfflour, zflourfflour, oilfcubefflour, maxoilcubezflourzcubefflour, oilcubezflourzcubefflour, oilcliniczflourfflour,  oilvasfcubefflour
             maxoilzflourzcubefcubefflour, maxoilcubecliniczflourzcubefcubefflour, oilcubefcubefflour, oilzflourzcubefcubefflour, oilcubecliniczflourzcubefflour  /

 flouronlyk(k) /zflour,  oilvaszflour, maxoilzflour, oilzflour,
            oilcliniczflour,     maxoilvaszflour, vaszflour , cliniczflour,
             maxoilcliniczflour /

 cubeonlyk(k) /cube,   maxoilcube,
           oilcube, oilcubevas, maxoilcubevas, cubevas, cubeclinic, oilcubeclinic,
           maxoilcubeclinic/

 flourcubek(k) /zflourzcube,    cubezflour, maxoilcubezflour,
            oilcubezflour, oilcubevaszflour ,
            cubevaszflour, maxoilcubevaszflour ,
            cubezflourzcube,   oilvaszflourzcube, maxoilzflourzcube,    maxoilcubezflourzcube, oilzflourzcube, oilcliniczflourzcube
            oilcubezflourzcube ,    oilcubevaszflourzcube, maxoilvaszflourzcube, vaszflourzcube, cliniczflourzcube, cubevaszflourzcube,
          maxoilcubevaszflourzcube     /
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
cov("cubezflour",j,t2)=cov("zflour",j,t2) ;
cov("maxoilcubezflour",j,t2)=cov("maxoilzflour",j,t2) ;
cov("oilcubezflour",j,t2)=cov("oilzflour",j,t2) ;
cov("oilcubevaszflour",j,t2)=cov("oilvaszflour",j,t2) ;
cov("cubevaszflour",j,t2)=cov("vaszflour",j,t2) ;
cov("maxoilcubevaszflour",j,t2)=cov("maxoilvaszflour",j,t2) ;
cov("oilcubecliniczflour",j,t2)=cov("oilcliniczflour",j,t2) ;
cov("maxoilcubecliniczflour",j,t2)=cov("maxoilcliniczflour",j,t2) ;
cov("cubezflourzcube",j,t2)=cov("zflour",j,t2) ;
cov("maxoilcubezflourzcube",j,t2)=cov("maxoilzflour",j,t2) ;
cov("oilcubezflourzcube",j,t2)=cov("oilzflour",j,t2) ;
cov("oilcubevaszflourzcube",j,t2)=cov("oilvaszflour",j,t2) ;
cov("oilcubecliniczflourzcube",j,t2)=cov("oilcliniczflour",j,t2) ;
cov("maxoilcubecliniczflourzcube",j,t2)=cov("maxoilcliniczflour",j,t2) ;
cov("cubezflourzcubefcubefflour",j,t2)=cov("zflourfflour",j,t2) ;
cov("cubezflourfcubefflour",j,t2)=cov("zflourfflour",j,t2) ;
cov("oilzflourzcubefcubefflour",j,t2)=cov("oilzflourfflour",j,t2);


cov("zcube",j,t2)=0                      ;
cov("zflourzcube",j,t2)=cov("zflour",j,t2) ;
cov("oilvaszflourzcube",j,t2)=cov("oilvaszflour",j,t2) ;
cov("maxoilcubezflourzcube",j,t2)=cov("maxoilzflour",j,t2) ;
cov("oilzflourzcube",j,t2)=cov("oilzflour",j,t2) ;

cov("fcube",j,t2)=0 ;
cov("oilfcube",j,t2)=cov("oil",j,t2) ;
cov("oilcubeclinicfcube",j,t2)=cov("oilclinic",j,t2) ;
cov("oilzflourfcubefflour",j,t2)=cov("oilzflourfflour",j,t2) ;
cov("maxoilzflourfcubefflour",j,t2)=cov("maxoilzflourfflour",j,t2) ;
cov("maxoilcliniczflourfcubefflour",j,t2)=cov("maxoilcliniczflourfflour",j,t2) ;





*Need to adjust all oil benefit interventions because input table has benefits for the first two years at 75% of target
cov("maxoil",j,t4)=cov("oil",j,t4) ;
cov("maxoilcube",j,t4)=cov("oilcube",j,t4) ;
cov("maxoilvas",j,t4)=cov("oilvas",j,t4) ;
cov("maxoilcubevas",j,t4)=cov("oilcubevas",j,t4) ;
cov("maxoilclinic",j,t4)=cov("oilclinic",j,t4) ;
cov("maxoilcubeclinic",j,t4)=cov("oilcubeclinic",j,t4) ;
cov("maxoilzflour",j,t4)=cov("oilzflour",j,t4) ;
cov("maxoilcubezflour",j,t4)=cov("oilcubezflour",j,t4) ;
cov("maxoilvaszflour",j,t4)=cov("oilvaszflour",j,t4) ;
cov("maxoilcliniczflour",j,t4)=cov("oilcliniczflour",j,t4) ;
cov("maxoilcubevaszflour",j,t4)=cov("oilcubevaszflour",j,t4) ;
cov("maxoilcubecliniczflour",j,t4)=cov("oilcubecliniczflour",j,t4) ;
cov("maxoilzflourzcube",j,t4)=cov("oilzflourzcube",j,t4) ;
cov("maxoilcubezflourzcube",j,t4)=cov("oilcubezflourzcube",j,t4) ;
cov("maxoilvaszflourzcube",j,t4)=cov("oilvaszflourzcube",j,t4) ;
cov("maxoilcliniczflourzcube",j,t4)=cov("oilcliniczflourzcube",j,t4) ;
cov("maxoilcubevaszflourzcube",j,t4)=cov("oilcubevaszflourzcube",j,t4) ;
cov("maxoilcubecliniczflourzcube",j,t4)=cov("oilcubecliniczflourzcube",j,t4) ;
cov("maxoilzflourfcubefflour",j,t4)=cov("oilzflourfcubefflour",j,t4);
cov("maxoilcliniczflourfcubefflour",j,t4)=cov("oilcliniczflourfcubefflour",j,t4);
            
display cov ;


totalbenefitsbau=sum(t,GAMMA(t)*(sum((j),cov("oilvaszflourfflour33",j,t))));
totalbenefits2=percben*totalbenefitsbau ;

display totalbenefitsbau, totalbenefits2, cost, cov ;

*Already added folate so get rid of other costs and benefits
*cost(cubek,j,t)=cost(cubek,j,t)*.92 ;
*cov("oilvaszflourfflour33",j,t)=0;
cov("zflourfflour33",j,t)=0;
cov("fflour33",j,t)=0;


Variables
X(k,j,t)      QUANTITY OF VA INTERVENTION ZERO OR ONE
*Y(k,j,t)      QUANTITY OF VA INTERVENTION ZERO OR ONE
XCOST         TOTAL COST FOR X VARIABLE INTERVENTIONS
XCOV          TOTAL COVERAGE FOR X VARIABLE INTERVENTIONS
Z             TOTAL COSTS
BEN           TOTAL COVERAGE
YESCUBE(j,t)   equal to 1 if there is cube in j at t
YESOIL(j,t)    equal to 1 if there is oil in j at t
YESMAXOIL(j,t) equal to 1 if there is oil in j at t
YESZCUBE(j,t)  equal to 1 if there is zinc cube in j at t
YESFCUBE(j,t)  equal to 1 if there is zinc cube in j at t
YESZFLOUR(j,t)  equal to 1 if there is flour in j at t
YESFFLOUR(j,t)  equal to 1 if there is flour in j at t
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
*onesy(j,t)               A CONSTRAINT ON THE NUMBER OF INTERVENTIONS THAT CAN BE CHOSEN FOR Y VARIABLES INTERVENTIONS
xcoveq(k,j,t)            THE AMOUNT OF COVERAGE FOR X
xcosteq(k,j,t)           THE AMOUNT OF COST FOR X

* Equations that force national interventions to be in all regions:
yescubeeq(j,t)       equation defining yescube>0 if there is cube in j
yeszcubeeq(j,t)       equation defining yeszcube>0 if there is zcube in j
yesfcubeeq(j,t)       equation defining yeszcube>0 if there is fcube in j
yeszfloureq(j,t)      equation defining yeszflour>0 if there is zflour in j
yesffloureq(j,t)      equation defining yesfflour>0 if there is fflour in j
yesoileq(j,t)        equation defining yesoil>0 if there is oil in j
yesmaxoileq(j,t)     equation defining yesmaxoil>0 if there is maxoil in j
allcubeeq(j,jj,t)    equation forcing cube to be either 1 or 0 in all regions
allzcubeeq(j,jj,t)    equation forcing zinc cube to be either 1 or 0 in all regions
allfcubeeq(j,jj,t)    equation forcing folate cube to be either 1 or 0 in all regions
allzfloureq(j,jj,t)   equation forcing zflour to be either 1 or 0 in all regions
allffloureq(j,jj,t)   equation forcing fflour to be either 1 or 0 in all regions
alloileq(j,jj,t)     equation forcing oil to be either 1 or 0 in all regions
allmaxoileq(j,jj,t)  equation forcing maxoil to be either 1 or 0 in all regions
alloileq2(j,t,tt)    equation forcing oil to be either 1 or 0 in all time periods
allmaxoileq2(j,t,tt) equation forcing maxoil to be either 1 or 0 in all time periods
allzfloureq2(j,t,tt) equation forcing zflour to be either 1 or 0 in all time periods
allffloureq2(j,t,tt) equation forcing fflour to be either 1 or 0 in all time periods
allcubeeq2(j,t,tt)   equation forcing cube to be either 1 or 0 in all time periods
allzcubeeq2(j,t,tt)  equation forcing zcube to be either 1 or 0 in all time periods
allfcubeeq2(j,t,tt)  equation forcing fcube to be either 1 or 0 in all time periods

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
*onesy(j,t)..           sum(k,y(k,j,t))=l=1;


* equations checking if there is flour, oil and cube anywhere:
yescubeeq(j,t)..       yescube(j,t) =e= sum((cubek),x(cubek,j,t)) ;
yeszcubeeq(j,t)..      yeszcube(j,t) =e= sum((zcubek),x(zcubek,j,t)) ;
yesfcubeeq(j,t)..      yesfcube(j,t) =e= sum((fcubek),x(fcubek,j,t)) ;
yeszfloureq(j,t)..     yeszflour(j,t) =e= sum((zflourk),x(zflourk,j,t)) ;
yesffloureq(j,t)..     yesfflour(j,t) =e= sum((fflourk),x(fflourk,j,t)) ;
yesoileq(j,t)..        yesoil(j,t) =e= sum((oilk),x(oilk,j,t)) ;
yesmaxoileq(j,t)..     yesmaxoil(j,t) =e= sum((maxoilk),x(maxoilk,j,t)) ;

* equations forcing there to be oil or cube everywhere if it is anywhere:
allcubeeq(j,jj,t)..          yescube(j,t) =e= yescube(jj,t) ;
allzcubeeq(j,jj,t)..         yeszcube(j,t) =e= yeszcube(jj,t) ;
allfcubeeq(j,jj,t)..         yesfcube(j,t) =e= yesfcube(jj,t) ;
alloileq(j,jj,t)..           yesoil(j,t) =e= yesoil(jj,t) ;
allmaxoileq(j,jj,t)..        yesmaxoil(j,t) =e= yesmaxoil(jj,t) ;
allzfloureq(j,jj,t)..         yeszflour(j,t) =e= yeszflour(jj,t) ;
allffloureq(j,jj,t)..         yesfflour(j,t) =e= yesfflour(jj,t) ;

* equations forcing there to be cube, in all times if it at anytime:
alloileq2(j,t2,tt)..         yesoil(j,tt) =e=yesoil(j,t2) ;
allmaxoileq2(j,t2,tt)..      yesmaxoil(j,tt) =e=yesmaxoil(j,t2) ;
allzfloureq2(j,t2,tt)..      yeszflour(j,tt) =e=yeszflour(j,t2) ;
allffloureq2(j,t2,tt)..      yesfflour(j,tt) =e=yesfflour(j,t2) ;
allcubeeq2(j,t2,tt)..        yescube(j,tt) =e=yescube(j,t2) ;
allzcubeeq2(j,t2,tt)..       yeszcube(j,tt) =e=yeszcube(j,t2)  ;
allfcubeeq2(j,t2,tt)..       yesfcube(j,tt) =e=yesfcube(j,t2)  ;


file lives_saved_low /lives_saved_low.csv/;
lives_saved_low.pc = 5;
put lives_saved_low;
put "intervention", "space", "time", "lives_saved" /;
loop((k,j,t),
     put k.tl, j.tl, t.tl, cov(k,j,t) /
);
putclose;

file costs_low /costs_low.csv/;
costs_low.pc = 5;
put costs_low;
put "intervention", "space", "time", "costs" /;
loop((k,j,t),
     put k.tl, j.tl, t.tl, cost(k,j,t) /
);
putclose;

Model nutrition /all/ ;
option minlp=BONMIN ;
Solve nutrition using minlp minimizing z ;
Display  x.l, z.l, ben.l, xcov.l, xcost.l, totalfunds, totalbenefits;

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
covbau(t)                =sum(j,cov("oilvaszflourfflour33",j,t))  ;
costbau(t)               =sum(j,cost("oilvaszflourfflour33",j,t))  ;
covbauspace(j)           =sum(t,cov("oilvaszflourfflour33",j,t))  ;
costbauspace(j)          =sum(t,cost("oilvaszflourfflour33",j,t))  ;
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
