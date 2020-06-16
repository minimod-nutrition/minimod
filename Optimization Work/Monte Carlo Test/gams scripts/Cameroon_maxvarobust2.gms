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
g groups
h test /fcube, fflour, fflourcube/
lab mean and standard deviation
;
set t2(t) just the first 3 years /1, 2, 3 /
    t3(t) years 4 to 10 /4,5,6,7,8,9,10/
* choose the number of draws (ex: change the second number from dr11 to dr499)
* nb: must be greater than 10 to allow for percentiles to be computed
    draw /dr0*dr9/ ;


parameter

costs(k,j)                costs for VA
costszinc(k,j)            costs for zinc
costsfolate(k,j)          costs for folate
costsb12(k,j)             costs for b12
costsiron(k,j)            costs for iron
coveragemf(k,j)           same parameter as coverage but only two indices (MF)
coveragerobust(k,j,lab)   means and standard deviations
coveragewra(k,j)          coverage for woman of reproductive age
coveragezinc(k,j)         coverage for zinc for children 6-59 months
coveragezincwra(k,j)      coverage for zinc for woman of reproductive age
coverageiron(k,j)         coverage for iron for children 6-59 months
coverageironwra(k,j)      coverage for iron for women of reproductive age
coveragetier1b(k,j)       coverage for VA tier1b
coveragefolate(k,j,lab)   coverage for folate for children 6-59 months
coveragefolatewra(k,j,lab) coverage for folate for woman of reproductive age
coverageb12(k,j)          coverage for b12 for children 6-59 months
coverageb12wra(k,j)       coverage for b12 for woman of reproductive age
fdeathsaverted(j,t,k)     deaths averted for children 6-59 months (VA using LiST) for Folate only
deathsaverted(j,t,k)      deaths averted for children 6-59 months (VA using LiST) Cube
deathsaverted2(j,t,k)     deaths averted for children 6-59 months (VA using LiST) Flour
deathsaverted3(j,t,k)     deaths averted for children 6-59 months (VA using LiST) Flourcube
deathsaverted4(j,t,k)     deaths averted for children 6-59 months (VA using LiST) No Folate
pop(t,j)                  Population of children aged 6-59 months
popwra(t,j)               Population of women of reproductive age
maize(t,j)                Maize costs
cdti(t,j)                 CDTI costs
hf(t,j)                   Health Facility costs
vapill(t,j)               Costs of VA capsules
dwpill(t,j)               Costs of DW tablets
mnppill(t,j)              Costs of MNP packets
zincpill(t,j)             Costs of Zinc tabs
;
* 1) Read in the data from all spreadsheets:
*--------------------------------------------------------------------------

* As a general rule, you should use one gdx file for each spreadsheet (keeps things clean)

* Read in the COSTS data from the COSTS spreadsheet
* the $call reads XL data and makes a .gdx file with it
$call "gdxxrw input=Cameroon_COSTS_hf_test.xlsx output=Cameroon_COSTS.gdx index=Indexcost!A2"
* the $gdxin opens the data loading procedure and calls the .gdx file we just made
$gdxin Cameroon_COSTS.gdx
$load k j costs
option costs:1:1:1;
display k, j, costs;

* Read in the COSTS data from the COSTS spreadsheet
* the $call reads XL data and makes a .gdx file with it
*$call "gdxxrw input=Cameroon_COSTS_zinc.xlsx output=Cameroon_COSTS_zinc.gdx index=Indexcost!A2"
* the $gdxin opens the data loading procedure and calls the .gdx file we just made
$gdxin Cameroon_COSTS_zinc.gdx
$load  costszinc
option costszinc:1:1:1;
display k, j, costszinc ;

* Read in the COSTS data from the COSTS spreadsheet
* the $call reads XL data and makes a .gdx file with it
*$call "gdxxrw input=Cameroon_COSTS_iron.xlsx output=Cameroon_COSTS_iron.gdx index=Indexcost!A2"
* the $gdxin opens the data loading procedure and calls the .gdx file we just made
$gdxin Cameroon_COSTS_iron.gdx
$load  costsiron
option costsiron:1:1:1;
display k, j, costsiron ;

* Read in the COSTS data from the COSTS spreadsheet
* the $call reads XL data and makes a .gdx file with it
*$call "gdxxrw input=Cameroon_COSTS_folate.xlsx output=Cameroon_COSTS_folate.gdx index=Indexcost!A2"
* the $gdxin opens the data loading procedure and calls the .gdx file we just made
$gdxin Cameroon_COSTS_folate.gdx
$load   costsfolate
option costsfolate:1:1:1;
display k, j, costsfolate ;

* Read in the COSTS data from the COSTS spreadsheet
* the $call reads XL data and makes a .gdx file with it
*$call "gdxxrw input=Cameroon_COSTS_b12.xlsx output=Cameroon_COSTS_b12.gdx index=Indexcost!A2"
* the $gdxin opens the data loading procedure and calls the .gdx file we just made
$gdxin Cameroon_COSTS_b12.gdx
$load  costsb12
option costsb12:1:1:1;
display k, j, costsb12 ;

* Input BENEFITS to nutrition interventions
*$call "gdxxrw input=benefits_1_13_2017_max.xlsx output=Cameroon_COVERAGE_mf.gdx index=Indexcoverage!A2"
$gdxin Cameroon_COVERAGE_mf.gdx
$load COVERAGEmf
option coveragemf:2:1:1 ;
display k, j, coveragemf ;

* Input BENEFITS to nutrition interventions
$call "gdxxrw input=benefits_8_13_2018_maxdata.xlsx output=Cameroon_COVERAGE_robust.gdx index=Indexcoverage!A2"
$gdxin Cameroon_COVERAGE_robust.gdx
$load lab COVERAGErobust
option coveragerobust:3:1:1 ;
display k, j, lab, coveragerobust ;

* Input BENEFITS to nutrition interventions for WRA
*$call "gdxxrw input=benefits_6_27_2015_wra.xlsx output=Cameroon_COVERAGE_wra.gdx index=Indexcoverage!A2"
$gdxin Cameroon_COVERAGE_wra.gdx
$load COVERAGEwra
option coveragewra:2:1:1 ;
display k, j, coveragewra ;

* Input BENEFITS to nutrition interventions Zinc Kids
*$call "gdxxrw input=zincbenefits_4_23_2015.xlsx output=Cameroon_COVERAGE_zinc.gdx index=Indexcoverage!A2"
$gdxin Cameroon_COVERAGE_zinc.gdx
$load COVERAGEzinc
option coveragezinc:2:1:1 ;
display k, j, coveragezinc ;


* Input BENEFITS to nutrition interventions for WRA
*$call "gdxxrw input=zincbenefits_4_23_2015_wra.xlsx output=Cameroon_COVERAGE_zincwra.gdx index=Indexcoverage!A2"
$gdxin Cameroon_COVERAGE_zincwra.gdx
$load COVERAGEzincwra
option coveragezincwra:2:1:1 ;
display k, j, coveragezincwra ;

* Input BENEFITS to nutrition interventions Iron Kids
*$call "gdxxrw input=ironbenefits_4_23_2015.xlsx output=Cameroon_COVERAGE_iron.gdx index=Indexcoverage!A2"
$gdxin Cameroon_COVERAGE_iron.gdx
$load COVERAGEiron
option coverageiron:2:1:1 ;
display k, j, coverageiron ;

* Input BENEFITS to nutrition interventions Iron WRA
*$call "gdxxrw input=ironbenefits_6_6_2016_wra.xlsx output=Cameroon_COVERAGE_ironwra.gdx index=Indexcoverage!A2"
$gdxin Cameroon_COVERAGE_ironwra.gdx
$load COVERAGEironwra
option coverageironwra:2:1:1 ;
display k, j, coverageironwra ;


* Input BENEFITS to nutrition interventions Folate Kids
*$call "gdxxrw input=folatebenefits_9_30_2016.xlsx output=Cameroon_COVERAGE_folate.gdx index=Indexcoverage!A2"
$gdxin Cameroon_COVERAGE_folate.gdx
$load COVERAGEfolate
option coveragefolate:3:1:1 ;
display k, j, lab, coveragefolate ;

* Input BENEFITS to nutrition interventions Folate WRA
*$call "gdxxrw input=folatebenefits_9_30_2016_wra.xlsx output=Cameroon_COVERAGE_folatewra.gdx index=Indexcoverage!A2"
$gdxin Cameroon_COVERAGE_folatewra.gdx
$load COVERAGEfolatewra
option coveragefolatewra:3:1:1 ;
display k, j, lab, coveragefolatewra ;

* Input BENEFITS to nutrition interventions B12 Kids
*$call "gdxxrw input=b12benefits_1_19_2016.xlsx output=Cameroon_COVERAGE_b12.gdx index=Indexcoverage!A2"
$gdxin Cameroon_COVERAGE_b12.gdx
$load COVERAGEb12
option coverageb12:2:1:1 ;
display k, j, coverageb12 ;

* Input BENEFITS to nutrition interventions B12 WRA
*$call "gdxxrw input=b12benefits_1_19_2016_wra.xlsx output=Cameroon_COVERAGE_b12wra.gdx index=Indexcoverage!A2"
$gdxin Cameroon_COVERAGE_b12wra.gdx
$load COVERAGEb12wra
option coverageb12:2:1:1 ;
display k, j, coverageb12wra ;

* Input LiST results to nutrition interventions  for folate
*$call "gdxxrw input=benefits_folateVA_list_new.xlsx output=Cameroon_fdeathsaverted.gdx index=Indexdeathsaverted!A2"
$gdxin Cameroon_fdeathsaverted.gdx
$load FDEATHSAVERTED
option fdeathsaverted:2:1:1 ;
display t, k, j, fdeathsaverted ;

* Input LiST results to nutrition interventions
*$call "gdxxrw input=benefits_folateVA_list.xlsx output=Cameroon_deathsaverted.gdx index=Indexdeathsaverted!A2"
$gdxin Cameroon_deathsaverted.gdx
$load DEATHSAVERTED
option deathsaverted:2:1:1 ;
display t, k, j, deathsaverted ;

*$call "gdxxrw input=benefits_folateVA_list2.xlsx output=Cameroon_deathsaverted2.gdx index=Indexdeathsaverted!A2"
$gdxin Cameroon_deathsaverted2.gdx
$load DEATHSAVERTED2
option deathsaverted2:2:1:1 ;
display t, k, j, deathsaverted2 ;

*$call "gdxxrw input=benefits_folateVA_list3.xlsx output=Cameroon_deathsaverted3.gdx index=Indexdeathsaverted!A2"
$gdxin Cameroon_deathsaverted3.gdx
$load DEATHSAVERTED3
option deathsaverted3:2:1:1 ;
display t, k, j, deathsaverted3 ;

*$call "gdxxrw input=benefits_folateVA_list4.xlsx output=Cameroon_deathsaverted4.gdx index=Indexdeathsaverted!A2"
$gdxin Cameroon_deathsaverted4.gdx
$load DEATHSAVERTED4
option deathsaverted4:2:1:1 ;
display t, k, j, deathsaverted4 ;

*Input POPULATION numbers
*$call "gdxxrw input=Age-group_pop_2015data.xlsx output=Cameroon_POP_mf.gdx index=Indexpop!A2"
$gdxin Cameroon_POP_mf.gdx
$load pop
display pop ;

*Input POPULATION numbers for wra
*$call "gdxxrw input=Age-group_pop_final.xlsx output=Cameroon_POP_wra.gdx index=Indexpopwra!A2"
$gdxin Cameroon_POP_wra.gdx
$load popwra
display popwra ;


* Input MAIZE COSTS
*$call "gdxxrw input=maize_11_13_2014.xlsx output=Cameroon_MAIZE_mf.gdx index=Indexmaize!A2"
$gdxin Cameroon_MAIZE_mf.gdx
$load MAIZE
display maize ;

* Input CDTI COSTS
*$call "gdxxrw input=cdti_6_8_2016.xlsx output=Cameroon_CDTI.gdx index=Indexcdti!A2"
$gdxin Cameroon_CDTI.gdx
$load CDTI
display cdti ;

* Input Health Facility COSTS
*$call "gdxxrw input=hf_6_8_2016.xlsx output=Cameroon_hf.gdx index=Indexhf!A2"
$gdxin Cameroon_hf.gdx
$load HF
display hf ;

* Input costs of VA capsules, DW, and Micronutriant packet costs
*$call "gdxxrw input=vadwmnp_4_2_2018.xlsx output=Cameroon_VADWMNP_mf.gdx index=IndexALL!A2"
$gdxin Cameroon_VADWMNP_mf.gdx
$load VAPILL DWPILL MNPPILL
display vapill, dwpill, mnppill ;

* Input costs of VA capsules, DW, and Micronutriant packet costs
*$call "gdxxrw input=zincmnp_12_29_2014.xlsx output=Cameroon_ZINCMNP_zinc.gdx index=IndexALL!A2"
$gdxin Cameroon_ZINCMNP_zinc.gdx
$load ZINCPILL
display zincpill ;



* 2) Define and compute all parameters for the model
*--------------------------------------------------------------------------
set bcck(k) /bcc, oilbcc, cubebcc, maizebcc, oilcubebcc, oilmaizebcc, cubemaizebcc, oilcubemaizebcc / ;

Scalar r discount rate /0/
totalfunds1 total funds available /35821703/
s loop value /1/
*totalfunds1 total funds available /10000034082.59954/
totalbenefits total benefits available /13458058/
vawght      VA weight                                    /1/
alphakids   VA weight for children 6-59months            /1/
betawra     VA weight for benefits for WRA               /0/
zincwght    Zinc weight                                  /0/
zincwghtc    Zinc weight costs                           /0/
zinckidwght  Zinc weight for children 6-59 months        /0/
zincwrawght  Zinc weight for wra                         /0/
ironwght         Iron weight                             /0/
ironkidwght      Iron weight for children 6-59 months    /0/
ironwrawght     Iron weight for wra                      /0/
folatewght      Folate weight                            /0/
folatekidwght   Folate weight for children 6-59 months   /0/
folatewrawght   Folate weight for wra                    /0/
b12wght          B12 weight                              /0/
b12kidwght       B12 weight for children 6-59 months     /0/
b12wrawght       B12 weight for wra                      /0/
includecdti      1 if including intervention cdti        /0/
includehf        1 if including intervention hf          /0/
includedw        1 if including intervention dw          /0/
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
totalbenefitsbau2(j)     TOTAL BENEFITS OF BAU* BY SPACE
totalbenefitsbau3(t)     TOTAL BENEFITS OF BAU* BY TIME
totalbenefitsbau4(j,t)   TOTAL BENEFITS OF BAU* BY SPACE & TIME
totalbenefitsbauva       TOTAL BENEFITS OF BAU* VA ONLY
totalbenefitsbauvakids   TOTAL BENEFITS OF BAU* VA KIDS
time(t)                  VECTOR OF TIME
intervention(k)          VECTOR OF INTERVENTIONS
c(k,j,t)                 TOTAL COSTS
c2(k,j,t)                TOTAL COSTS 2
c3(k,j,t)                TOTAL COSTS 3
czinc(k,j,t)             TOTAL COSTS ZINC
czinc2(k,j,t)            TOTAL COSTS ZINC 2
czinc3(k,j,t)            TOTAL COSTS ZINC 3
ciron(k,j,t)             TOTAL COSTS IRON
ciron2(k,j,t)            TOTAL COSTS IRON 2
ciron3(k,j,t)            TOTAL COSTS IRON 3
cfolate(k,j,t)           TOTAL COSTS FOLATE
cfolate2(k,j,t)          TOTAL COSTS FOLATE 2
cfolate3(k,j,t)          TOTAL COSTS FOLATE 3
cb12(k,j,t)              TOTAL COSTS B12
cb122(k,j,t)             TOTAL COSTS B12 2
cb123(k,j,t)             TOTAL COSTS B12 3
cmaize(k,j,t)            COSTS FOR MAIZE
cmaize2(k,j,t)           COSTS FOR MAIZE2 FOR ROBUSTNESS CHECKS
cmaize3(k,j,t)           COSTS FOR MAIZE3 FOR ROBUSTNESS CHECKS
ccdti(k,j,t)             COSTS FOR CDTI
chf(k,j,t)               COSTS FOR HEALTH FACILITIES
covlist(k,j,t)           COVERAGE MATRIX FROM LiST RESULTS
covwra(k,j,t)            COVERAGE FOR WOMEN OF REPRODUCTIVE AGE
covwra2(k,j,t)           COVERAGE FOR WOMEN OF REPRODUCTIVE AGE 2
covwra3(k,j,t)           COVERAGE FOR WOMEN OF REPRODUCTIVE AGE 3
covzinc(k,j,t)           COVERAGE MATRIX FOR ZINC
covzinc2(k,j,t)          COVERAGE MATRIX FOR ZINC 2
covzinc3(k,j,t)          COVERAGE MATRIX FOR ZINC 3
coviron(k,j,t)           COVERAGE MATRIX FOR IRON
coviron2(k,j,t)          COVERAGE MATRIX FOR IRON 2
coviron3(k,j,t)          COVERAGE MATRIX FOR IRON 3
covironwra(k,j,t)        COVERAGE MATRIX FOR IRON WRA
covironwra2(k,j,t)       COVERAGE MATRIX FOR IRON WRA 2
covironwra3(k,j,t)       COVERAGE MATRIX FOR IRON WRA 3
covfolate(k,j,t)         COVERAGE MATRIX FOR FOLATE
covfolate2(k,j,t)        COVERAGE MATRIX FOR FOLATE 2
covfolate3(k,j,t)        COVERAGE MATRIX FOR FOLATE 3
covfolatewra(k,j,t)      COVERAGE MATRIX FOR FOLATE WRA
covfolatewra2(k,j,t)     COVERAGE MATRIX FOR FOLATE WRA 2
covfolatewra3(k,j,t)     COVERAGE MATRIX FOR FOLATE WRA 3
covb12(k,j,t)            COVERAGE MATRIX FOR B12
covb122(k,j,t)           COVERAGE MATRIX FOR B12 2
covb123(k,j,t)           COVERAGE MATRIX FOR B12 3
covb12wra(k,j,t)         COVERAGE MATRIX FOR B12 WRA
covb12wra2(k,j,t)        COVERAGE MATRIX FOR B12 WRA 2
covb12wra3(k,j,t)        COVERAGE MATRIX FOR B12 WRA 3
covzincwra(k,j,t)        COVERAGE FOR WOMEN OF REPRODUCTIVE AGE FOR ZINC
covzincwra2(k,j,t)       COVERAGE FOR WOMEN OF REPRODUCTIVE AGE FOR ZINC 2
covzincwra3(k,j,t)       COVERAGE FOR WOMEN OF REPRODUCTIVE AGE FOR ZINC 3
cov(k,j,t)               COVERAGE MATRIX
cov2(k,j,t)              COVERAGE MATRIX 2
cov3(k,j,t)              COVERAGE MATRIX 3
covtier1b(k,j,t)         COVERAGE MATRIX for Tier 1b
test(h)                  Testing
covnew(k,j,t)              COVERAGE MATRIX NEW
costnew(k,j,t)             COST MATRIX NEW
cstart(k,j,t)              COST MATRIX START
crobust(k,j,t)             COST MATRIX ROBUST
tcosttest(h,k,j,t)       COST MATRIX TEST
tcovtest(h,k,j,t)        COV MATRIX TEST
;
*for (s=1 to 5 by 1,
*         test(h)=s;
*         display test;
*);


*coveragemf(bcck,j) = coveragemf(bcck,j)*1.25 ;
*costs(bcck,j) = costs(bcck,j)/2 ;
display coveragemf ;

* Computing discount rates for costs and benefits (may differ if interest rates differ)
DISCOUNT    = 1/(1+INTLEND);
BETA(t)     = DISCOUNT**(ORD(t)-1) ;
DISCOUNT2    = 1/(1+INTLEND2);
GAMMA(t)     = DISCOUNT2**(ORD(t)-1) ;

* Defining constraint levels
totalfunds = totalfunds1*1;
*totalbenefits2=sum(t,GAMMA(t)*((totalbenefits*1)/10));

* Make the coverage and costs parameters
cov(k,j,t)       = coveragerobust(k,j,"mean")*pop(t,j) ;
display cov;
*Max oil simulation 44%-72%-100%
cov("fortoil",j,"1") = coveragerobust("dwoil",j,"mean")*pop("1",j);
cov("capoil",j,"1") = coveragerobust("capdwoil",j,"mean")*pop("1",j);
cov("oilcube",j,"1") = coveragerobust("dwoilcube",j,"mean")*pop("1",j);
cov("capoilcube",j,"1") = coveragerobust("capdwoilcube",j,"mean")*pop("1",j);
cov("capoilmaize",j,"1") = coveragerobust("capdwoilmaize",j,"mean")*pop("1",j);
cov("oilmaize",j,"1") = coveragerobust("dwoilmaize",j,"mean")*pop("1",j);
cov("oilcubemaize",j,"1") = coveragerobust("dwoilcubemaize",j,"mean")*pop("1",j);
cov("capoilcubemaize",j,"1") = coveragerobust("capdwoilcubemaize",j,"mean")*pop("1",j);
cov("fortoil","south","2") = 0.188647039*pop("2","south");
cov("fortoil","north","2") = 0.184657986*pop("2","north");
cov("fortoil","cities","2") = 0.361048462*pop("2","cities");
cov("capoil","south","2") = 0.271910918*pop("2","south");
cov("capoil","north","2") = 0.552711992*pop("2","north");
cov("capoil","cities","2") = 0.429750048*pop("2","cities");
cov("oilcube","south","2") = 0.317578384*pop("2","south");
cov("oilcube","north","2") = 0.452445346*pop("2","north");
cov("oilcube","cities","2") = 0.460061855*pop("2","cities");
cov("capoilcube","south","2") = 0.335812702*pop("2","south");
cov("capoilcube","north","2") = 0.66038935*pop("2","north");
cov("capoilcube","cities","2") = 0.481598393*pop("2","cities");
cov("capoilmaize","south","2") = 0.281736205*pop("2","south");
cov("capoilmaize","north","2") = 0.449118915*pop("2","north");
cov("capoilmaize","cities","2") = 0.381499444*pop("2","cities");
cov("oilmaize","south","2") = 0.193206296*pop("2","south");
cov("oilmaize","north","2") = 0.298684737*pop("2","north");
cov("oilmaize","cities","2") = 0.314661303*pop("2","cities");
cov("oilcubemaize","south","2") = 0.281736205*pop("2","south");
cov("oilcubemaize","north","2") = 0.449118915*pop("2","north");
cov("oilcubemaize","cities","2") = 0.381499444*pop("2","cities");
cov("capoilcubemaize","south","2") = 0.331342794*pop("2","south");
cov("capoilcubemaize","north","2") = 0.662643196*pop("2","north");
cov("capoilcubemaize","cities","2") = 0.471177607*pop("2","cities");
display cov ;


covwra(k,j,t)    = coveragewra(k,j)*popwra(t,j) ;
covzinc(k,j,t)   = coveragezinc(k,j)*pop(t,j) ;
coviron(k,j,t)   = coverageiron(k,j)*pop(t,j) ;
covironwra(k,j,t)= coverageironwra(k,j)*popwra(t,j);
covfolate(k,j,t) = coveragefolate(k,j,"mean")*pop(t,j) ;
covfolatewra(k,j,t) = coveragefolatewra(k,j,"mean")*popwra(t,j) ;
covb12(k,j,t)    = coverageb12(k,j)*pop(t,j) ;
covb12wra(k,j,t) = coverageb12wra(k,j)*popwra(t,j) ;
covzincwra(k,j,t)= coveragezincwra(k,j)*popwra(t,j) ;

covlist(k,j,t)   =deathsaverted(j,t,k);
c(k,j,t)         =costs(k,j);
cmaize(k,j,t)    =maize(t,j);
czinc(k,j,t)     =costszinc(k,j);
ciron(k,j,t)     =costsiron(k,j);
cfolate(k,j,t)   =costsfolate(k,j);
cb12(k,j,t)      =costsb12(k,j);
ccdti(k,j,t)     =cdti(t,j);
chf(k,j,t)       =hf(t,j);

* versions "2" and "3" are just subsets for years 1/3 and 4/10
c2(k,j,t2)        = c(k,j,t2);
c3(k,j,t3)        = c(k,j,t3);
czinc2(k,j,t2)    = czinc(k,j,t2);
czinc3(k,j,t3)    = czinc(k,j,t3);
ciron2(k,j,t2)    = ciron(k,j,t2);
ciron3(k,j,t3)    = ciron(k,j,t3);
cfolate2(k,j,t2)  = cfolate(k,j,t2);
cfolate3(k,j,t3)  = cfolate(k,j,t3);
cb122(k,j,t2)     = cb12(k,j,t2);
cb123(k,j,t3)     = cb12(k,j,t3);
cov2(k,j,t2)      = cov(k,j,t2) ;
cov3(k,j,t3)      = cov(k,j,t3) ;
covwra2(k,j,t2)   = covwra(k,j,t2);
covwra3(k,j,t3)   = covwra(k,j,t3);
covzinc2(k,j,t2)  = covzinc(k,j,t2);
covzinc3(k,j,t3)  = covzinc(k,j,t3);
coviron2(k,j,t2)  = coviron(k,j,t2);
coviron3(k,j,t3)  = coviron(k,j,t3);
covironwra2(k,j,t2) = covironwra(k,j,t2);
covironwra3(k,j,t3) = covironwra(k,j,t3);
covfolate2(k,j,t2)  = covfolate(k,j,t2);
covfolate3(k,j,t3)  = covfolate(k,j,t3);
covfolatewra2(k,j,t2)  = covfolatewra(k,j,t2);
covfolatewra3(k,j,t3)  = covfolatewra(k,j,t3);
covb122(k,j,t2)     = covb12(k,j,t2);
covb123(k,j,t3)     = covb12(k,j,t3);
covb12wra2(k,j,t2)  = covb12wra(k,j,t2);
covb12wra3(k,j,t3)  = covb12wra(k,j,t3);
covzincwra2(k,j,t2) = covzincwra(k,j,t2);
covzincwra3(k,j,t3) = covzincwra(k,j,t3);


display cov, cov2, cov3, covwra, covwra2, covwra3, covzinc, covzinc2, covzinc3, covfolate, covfolate2, covfolate3, covb12wra, covb12wra2,  covb12wra3,
covzincwra, covzincwra2, covzincwra3, coviron, covironwra2, covironwra3 ;

display c, c2, c3, czinc, czinc2, czinc3, covlist;


* MAKE ONE SINGLE COST PARAMETER and ONE SINGLE COVERAGE PARAMETER
*-------------------------------------------------------------------
set oilk(k) /fortoil, capoil,  mnpoil, oilcube, oilcdti, oilhf,
             capmnpoil,  capoilcube, mnpoilcube, oilmaizehf,
              oilcubecdti, oilcubehf, capmnpoilcube,
              oilmaize, oilcubemaize, capoilmaize,
              oilmnpmaize, capoilmnpmaize, dwoilmnpmaize, capoilcubemaize,
              oilcubemnpmaize,  oilcubemaizecdti, oilcubemaizehf,
              capoilcubemnpmaize, oilbcc, oilcubebcc, oilmaizebcc, oilcubemaizebcc /


set cubek(k) /fortcube,  oilcube, cubecdti, cubehf,
             capcube, dwcube, mnpcube, mnpdwcube, capmnpcube, capdwcube, capdwmnpcube, oilcubecdti, oilcubehf,
              capoilcube, mnpoilcube, dwoilcube, capdwoilcube, capmnpoilcube, dwmnpoilcube, capdwmnpoilcube,
               cubemaize, oilcubemaize, capcubemaize, dwcubemaize,   cubemaizehf,
               cubemnpmaize, capdwcubemaize, capcubemnpmaize, capoilcubemaize, oilcubemaizecdti, oilcubemaizehf,
               dwoilcubemaize, dwcubemnpmaize, oilcubemnpmaize, capdwoilcubemaize, capdwcubemnpmaize,
               capoilcubemnpmaize, dwoilcubemnpmaize, capdwoilcubemnpmaize, cubebcc, oilcubebcc, cubemaizebcc, oilcubemaizebcc /
* flourcube,
*            suppcube, mnpsuppcube, mnpflourcube, suppflourcube, mnpsuppflourcube /

set maizek(k) /maize, oilmaize, cubemaize, capmaize, dwmaize, mnpmaize, maizecdti, oilmaizecdti, cubemaizecdti,
               maizehf, oilmaizehf, cubemaizehf, oilcubemaize,
               capoilmaize, dwoilmaize, capdwmaize, capcubemaize, dwcubemaize, capmnpmaize,
               dwmnpmaize, oilmnpmaize, cubemnpmaize, oilcubemaizecdti, oilcubemaizehf, capdwcubemaize, capcubemnpmaize, capdwmnpmaize,
               capdwoilmaize, capoilcubemaize, capoilmnpmaize,  dwoilcubemaize,
               dwoilmnpmaize, dwcubemnpmaize, oilcubemnpmaize, capdwoilmnpmaize, capdwoilcubemaize,
               capdwcubemnpmaize, capoilcubemnpmaize, dwoilcubemnpmaize, capdwoilcubemnpmaize, maizebcc, oilmaizebcc, cubemaizebcc, oilcubemaizebcc   /

set natk(k) /fortoil, fortcube,
              maize, oilcube, oilmaize, cubemaize, oilcubemaize   /

set flourk(k) /flour, flourcube,
             suppflour, mnpflour, mnpsuppflour, mnpflourcube, suppflourcube, mnpsuppflourcube/

set folateflourk(k) /flour, mnpflour, flourcube/

set ironflourk(k) /flour, flourcube, mnpflour, mnpflourcube/

set b12flourk(k) /flour, flourcube, mnpflour/

set b12cubek(k) /cube, flourcube, mnpcube/

set zinccubek(k) /cube,  flourcube,
                 suppcube, mnpcube, mnpsuppcube, mnpflourcube, suppflourcube, mnpsuppflourcube /

set ironcubek(k) /cube,  flourcube, mnpcube, mnpflourcube /

set folatecubek(k) /fortcube, flourcube /

set mnpk(k) /mnp, capmnp, dwmnp, mnpoil, capdwmnp, capmnpoil, dwmnpoil, mnpdwcube, capmnpcube, capdwmnpcube,
             mnpoilcube, capmnpoilcube, dwmnpoilcube, capdwmnpoilcube,  mnpmaize, capmnpmaize,
               dwmnpmaize, oilmnpmaize, cubemnpmaize, capcubemnpmaize, capdwmnpmaize,
               dwoilmnpmaize, dwcubemnpmaize, oilcubemnpmaize, capdwoilmnpmaize,
               capdwcubemnpmaize, capoilcubemnpmaize, dwoilcubemnpmaize, capdwoilcubemnpmaize,
                 mnpcube, mnpsupp, mnpflour, mnpsuppflour, mnpsuppcube, mnpflourcube, mnpsuppflourcube  /

set capk(k) /capsules, capoil, capcube, capmnp, capdw, capmaize,
             capdwoil, capdwcube, capoilcube, capoilmaize, capdwmnp, capmnpoil, capmnpcube, capdwmaize, capcubemaize, capmnpmaize,
             capdwmnpcube, capmnpoilcube, capdwoilcube, capdwmnpoil, capdwoilmaize, capdwcubemaize, capdwmnpmaize, capoilcubemaize, capoilmnpmaize, capcubemnpmaize
             capdwmnpoilcube, capdwoilmnpmaize, capdwoilcubemaize, capdwcubemnpmaize, capoilcubemnpmaize,
             capdwoilcubemnpmaize  /

set dwk(k) /dwoil, dwoilcube, capdwoilcube, dwcube, capdwoil, capdwcube, dwmaize, dwoilmaize, capdwmaize, dwcubemaize, capdwoilmaize, dwoilcubemaize, capdwoilcubemaize  /

set mnpzinck(k) /mnp, mnpcube, mnpsupp, mnpflour, mnpsuppflour, mnpsuppcube, mnpflourcube, mnpsuppflourcube  /

set cdtik(k) /cdti, oilcdti, cubecdti, maizecdti, oilcubecdti, oilmaizecdti, cubemaizecdti, oilcubemaizecdti /

set hfk(k) /hf, oilhf, cubehf, maizehf, oilcubehf, oilmaizehf, cubemaizehf, oilcubemaizehf /

Parameter tcost(k,j,t)           total costs
          tcostzinc(k,j,t)       total cost for zinc
          tcostiron(k,j,t)       total cost for iron
          tcostfolate(k,j,t)     total cost for folate
          tcostfolate2(k,j,t)    total cost for folate 2
          tcostb12(k,j,t)        total cost for b12
          tcov(k,j,t)            total cov
          tcovwra(k,j,t)         total covwra
          tcovzinc(k,j,t)        total cov
          tcovzincwra(k,j,t)     total covwra
          tcoviron(k,j,t)        total cov for iron
          tcovironwra(k,j,t)     total cov for iron wra
          tcovfolate(k,j,t)      total cov for folate
          tcovfolatewra(k,j,t)   total cov for folate wra
          tcovb12(k,j,t)         total cov for b12
          tcovb12wra(k,j,t)      total cov for b12 wra
          tcovcube(k,j,t)        total cov for folate cube
          tcovflour(k,j,t)       total cov for folate flour
          tcovflourcube(k,j,t)   total cov for folate flour cube
          tcovnone(k,j,t)        total cov for no folate only VA combinations
          fcov(k,j,t)            total cov for folate cube
* Parameters for each draw
          totalcost_d(draw)      total costs for each draw
          totalben_d(draw)       total benefits for each draw
          totalcb_d(draw)        total cost per unit -child or WRA;

*cov(cubek,j,t) = cov(cubek,j,t)+fdeathsaverted(j,t,"fortcube");
*cov2(cubek,j,t2)=cov2(cubek,j,t2)+fdeathsaverted(j,t2,"fortcube") ;
*cov3(cubek,j,t3)=cov3(cubek,j,t3)+fdeathsaverted(j,t3,"fortcube") ;
fcov("fortcube",j,t3)=fdeathsaverted(j,t3,"fortcube") ;
cov("flour",j,t) =fdeathsaverted(j,t,"flour");
cov2("flour",j,t2)=fdeathsaverted(j,t2,"flour") ;
cov3("flour",j,t3)=fdeathsaverted(j,t3,"flour") ;
cov("flourcube",j,t) =fdeathsaverted(j,t,"flourcube");
cov2("flourcube",j,t2)=fdeathsaverted(j,t2,"flourcube") ;
cov3("flourcube",j,t3)=fdeathsaverted(j,t3,"flourcube") ;

display cov, cov2, cov3, fcov;
* Define all cost combinations
* cost - subnational - VA:
tcost("capsules",j,t)      =c("capsules",j,t)+vapill(t,j);
tcost("deworming",j,t)     =c("deworming",j,t)+dwpill(t,j);
tcost("mnp",j,t)           =c("mnp",j,t)+mnppill(t,j);
tcost("capdw",j,t)         =c("capdw",j,t)+vapill(t,j)+dwpill(t,j);
tcost("capMNP",j,t)        =c("capmnp",j,t)+vapill(t,j)+mnppill(t,j);
tcost("dwmnp",j,t)         =c("dwmnp",j,t)+mnppill(t,j)+dwpill(t,j);
tcost("capdwmnp",j,t)      =c("capdwmnp",j,t)+vapill(t,j)+dwpill(t,j)+mnppill(t,j);
tcost("cdti",j,t)          =c("cdti",j,t);
tcost("hf",j,t)            =c("hf",j,t);
tcost("bcc",j,t)           =c("bcc",j,t)+vapill(t,j);

* cost - subnational - zinc:
tcostzinc("supp",j,t)            =czinc("supp",j,t)+zincpill(t,j);
tcostzinc("mnp",j,t)             =czinc("mnp",j,t)+mnppill(t,j);
tcostzinc("mnpsupp",j,t)         =czinc("mnpsupp",j,t)+zincpill(t,j)+mnppill(t,j);

* cost - subnational - iron:
tcostiron("mnp",j,t)             =ciron("mnp",j,t)+mnppill(t,j);

* cost - subnational - folate:
tcostfolate("mnp",j,t)           =cfolate("mnp",j,t)+mnppill(t,j);

* cost - subnational - b12:
tcostb12("mnp",j,t)              =cb12("mnp",j,t)+mnppill(t,j);

* cost - national - VA:
tcost("fortoil",j,t)       =c("fortoil",j,t);
tcost("fortcube",j,t)      =c2("fortcube",j,t)+c3("fortcube2",j,t);
*tcost("fortcube",j,t)      =c("fortcube2",j,t);
tcost("maize",j,t)         =cmaize("maize",j,t);
tcost("cdti",j,t)          =ccdti("cdti",j,t);
tcost("hf",j,t)            =chf("hf",j,t);
tcost("oilcube",j,t)       =c2("oilcube",j,t)+c3("oilcube2",j,t);
*tcost("oilcube",j,t)       =c("oilcube2",j,t);
tcost("oilmaize",j,t)      =cmaize("maize",j,t)+c("fortoil",j,t);
tcost("cubemaize",j,t)     =cmaize("maize",j,t)+c2("fortcube",j,t)+c3("fortcube2",j,t);
tcost("oilcubemaize",j,t)  =cmaize("maize",j,t)+c2("oilcube",j,t)+c3("oilcube2",j,t);

* cost - national - zinc:
tcostzinc("flour",j,t)       =czinc("flour",j,t);
tcostzinc("cube",j,t)        =czinc2("cube",j,t)+czinc3("cube2",j,t);
tcostzinc("flourcube",j,t)   =czinc2("flourcube",j,t)+czinc3("flourcube2",j,t);

* cost - national - zinc:
tcostiron("flour",j,t)       =ciron("flour",j,t);
tcostiron("cube",j,t)        =ciron2("cube",j,t)+ciron3("cube2",j,t);
tcostiron("flourcube",j,t)   =ciron2("flourcube",j,t)+ciron3("flourcube2",j,t);


* cost - national - folate:
tcostfolate("flour",j,t)        =cfolate("flour",j,t);
tcostfolate("fortcube",j,t)     =cfolate2("fortcube",j,t)+cfolate3("fortcube2",j,t);
tcostfolate("flourcube",j,t)    =cfolate2("flourcube",j,t)+cfolate3("flourcube2",j,t);
*tcost("flour",j,t)              =tcostfolate("flour",j,t) ;
*tcost("flourcube",j,t)          =tcostfolate("flourcube",j,t) ;

* cost - national - b12:
tcostb12("flour",j,t)        =cb12("flour",j,t);
tcostb12("cube",j,t)         =cb122("cube",j,t)+cb123("cube2",j,t);
tcostb12("flourcube",j,t)    =cb122("flourcube",j,t)+cb123("flourcube2",j,t);

* cov - subnational - VA
tcov("capsules",j,t)  =cov("capsules",j,t);
tcov("deworming",j,t) =cov("deworming",j,t);
tcov("mnp",j,t)       =cov("mnp",j,t);
tcov("capdw",j,t)     =cov("capdw",j,t);
tcov("capMNP",j,t)    =cov("capmnp",j,t);
tcov("dwmnp",j,t)     =cov("dwmnp",j,t);
tcov("capdwmnp",j,t)  =cov("capdwmnp",j,t);
tcov("cdti",j,t)      =cov("cdti",j,t);
tcov("bcc",j,t)       =cov("bcc",j,t);

* cov - subnational - zinc
tcovzinc("supp",j,t)      =covzinc("supp",j,t);
tcovzinc("mnp",j,t)       =covzinc("mnp",j,t);
tcovzinc("mnpsupp",j,t)   =covzinc("mnpsupp",j,t);

* cov - subnational - iron
tcoviron("mnp",j,t)     =coviron("mnp",j,t);

* cov - subnational - folate
tcovfolate("mnp",j,t)     =covfolate("mnp",j,t);

* cov - subnational - b12
tcovb12("mnp",j,t)       =covb12("mnp",j,t);

* cov - national - VA
tcov("fortoil",j,t)      =cov("fortoil",j,t);
tcov("fortcube",j,t)     =cov3("fortcube",j,t);
tcov("maize",j,t)        =cov3("maize",j,t);
tcov("oilcube",j,t)      =cov2("fortoil",j,t)+cov3("oilcube",j,t);
tcov("oilmaize",j,t)     =cov2("fortoil",j,t)+cov3("oilmaize",j,t);
tcov("cubemaize",j,t)    =cov3("cubemaize",j,t);
tcov("oilcubemaize",j,t) =cov2("fortoil",j,t)+cov3("oilcubemaize",j,t);
*tcov("flour",j,t)        =cov("flour",j,t);
*tcov("flourcube",j,t)    =cov2("flour",j,t)+cov3("flourcube",j,t);

* cov - national - zinc
tcovzinc("flour",j,t)         =covzinc("flour",j,t);
tcovzinc("cube",j,t)          =covzinc3("cube",j,t);
tcovzinc("flourcube",j,t)     =covzinc2("flour",j,t)+covzinc3("flourcube",j,t);

* cov - national - zinc
tcoviron("flour",j,t)         =coviron("flour",j,t);
tcoviron("cube",j,t)          =coviron3("cube",j,t);
tcoviron("flourcube",j,t)     =coviron2("flour",j,t)+coviron3("flourcube",j,t);

* cov - national - folate
tcovfolate("flour",j,t)       =covfolate("flour",j,t);
tcovfolate("fortcube",j,t)    =covfolate3("fortcube",j,t);
tcovfolate("flourcube",j,t)   =covfolate2("flour",j,t)+covfolate3("flourcube",j,t);

* cov - national - folate wra
tcovfolatewra("flour",j,t)       =covfolatewra("flour",j,t);
tcovfolatewra("fortcube",j,t)    =covfolatewra3("fortcube",j,t);
tcovfolatewra("flourcube",j,t)   =covfolatewra2("flour",j,t)+covfolatewra3("flourcube",j,t);

* cov - national - b12
tcovb12("flour",j,t)         =covb12("flour",j,t);
tcovb12("cube",j,t)          =covb123("cube",j,t);
tcovb12("flourcube",j,t)     =covb122("flour",j,t)+covb123("flourcube",j,t);

* cov - national - b12 wra
tcovb12wra("flour",j,t)         =covb12wra("flour",j,t);
tcovb12wra("cube",j,t)          =covb12wra3("cube",j,t);
tcovb12wra("flourcube",j,t)     =covb12wra2("flour",j,t)+covb12wra3("flourcube",j,t);

* cov - national - zinc - wra
tcovzincwra("flour",j,t)      =covzincwra("flour",j,t);
tcovzincwra("cube",j,t)       =covzincwra3("cube",j,t);
tcovzincwra("flourcube",j,t)  =covzincwra2("flour",j,t)+covzincwra3("flourcube",j,t);

* cov - national - b12 wra
tcovironwra("flour",j,t)         =covironwra("flour",j,t);
tcovironwra("cube",j,t)          =covironwra3("cube",j,t);
tcovironwra("flourcube",j,t)     =covironwra2("flour",j,t)+covironwra3("flourcube",j,t);

* covwra - national - VA:
tcovwra("fortoil",j,t)      =covwra("fortoil",j,t);
tcovwra("fortcube",j,t)     =covwra3("fortcube",j,t);
tcovwra("maize",j,t)        =covwra3("maize",j,t);
tcovwra("oilcube",j,t)      =covwra2("fortoil",j,t)+covwra3("oilcube",j,t);
tcovwra("oilmaize",j,t)     =covwra2("fortoil",j,t)+covwra3("oilmaize",j,t);
tcovwra("cubemaize",j,t)    =covwra3("cubemaize",j,t);
tcovwra("oilcubemaize",j,t) =covwra2("fortoil",j,t)+covwra3("oilcubemaize",j,t);

* These are all the mixed combinations costs (subnational with national) for VA
tcost("capoil",j,t)         =c("capoil",j,t)+vapill(t,j);
tcost("capcube",j,t)        =c2("capcube",j,t)+c3("capcube2",j,t)+vapill(t,j);
*tcost("capcube",j,t)       =c2("capcube2",j,t)+c3("capcube2",j,t)+vapill(t,j);
tcost("capmaize",j,t)       =cmaize("maize",j,t)+c("capsules",j,t)+vapill(t,j);
tcost("dwoil",j,t)          =c("dwoil",j,t)+dwpill(t,j);
tcost("dwcube",j,t)         =c2("dwcube",j,t)+c3("dwcube2",j,t)+dwpill(t,j);
*tcost("dwcube",j,t)        =c2("dwcube2",j,t)+c3("dwcube2",j,t);
tcost("dwmaize",j,t)        =cmaize("maize",j,t)+c("deworming",j,t)+dwpill(t,j);
tcost("mnpoil",j,t)         =c("mnpoil",j,t)+mnppill(t,j);
tcost("mnpcube",j,t)        =c2("mnpcube",j,t)+c3("mnpcube2",j,t)+mnppill(t,j);
*tcost("mnpcube",j,t)        =c2("mnpcube2",j,t)+c3("mnpcube2",j,t)+mnppill(t,j);
tcost("mnpmaize",j,t)       =cmaize("maize",j,t)+c("mnp",j,t)+mnppill(t,j);
tcost("oilcdti",j,t)        =ccdti("cdti",j,t)+c("fortoil",j,t);
tcost("cubecdti",j,t)       =ccdti("cdti",j,t)+c2("fortcube",j,t)+c3("fortcube2",j,t);
tcost("maizecdti",j,t)      =cmaize("maize",j,t)+ccdti("cdti",j,t);
tcost("oilhf",j,t)          =chf("hf",j,t)+c("fortoil",j,t);
tcost("cubehf",j,t)         =chf("hf",j,t)+c2("fortcube",j,t)+c3("fortcube2",j,t);
tcost("maizehf",j,t)        =cmaize("maize",j,t)+chf("hf",j,t);
tcost("oilbcc",j,t)         =c("oilbcc",j,t)+vapill(t,j);
tcost("cubebcc",j,t)        =c2("cubebcc",j,t)+c3("cubebcc2",j,t)+vapill(t,j);
tcost("maizebcc",j,t)       =cmaize("maize",j,t)+c("bcc",j,t)+vapill(t,j);

tcost("capoilcube",j,t)    =c2("capoilcube",j,t)+c3("capoilcube2",j,t)+vapill(t,j);
*tcost("capoilcube",j,t)    =c2("capoilcube2",j,t)+c3("capoilcube2",j,t)+vapill(t,j);
tcost("dwoilcube",j,t)     =c2("dwoilcube",j,t)+c3("dwoilcube2",j,t)+dwpill(t,j);
*tcost("dwoilcube",j,t)     =c2("dwoilcube2",j,t)+c3("dwoilcube2",j,t)+dwpill(t,j);
tcost("mnpoilcube",j,t)    =c2("mnpoilcube",j,t)+c3("mnpoilcube2",j,t)+mnppill(t,j);
*tcost("mnpoilcube",j,t)    =c2("mnpoilcube2",j,t)+c3("mnpoilcube2",j,t)+mnppill(t,j);
tcost("capdwcube",j,t)     =c2("capdwcube",j,t)+c3("capdwcube2",j,t)+vapill(t,j)+dwpill(t,j);
*tcost("capdwcube",j,t)     =c2("capdwcube2",j,t)+c3("capdwcube2",j,t)+vapill(t,j)+dwpill(t,j);
tcost("capdwoil",j,t)      =c("capdwoil",j,t)+vapill(t,j);
tcost("capdwmaize",j,t)    =cmaize("maize",j,t)+c("capdw",j,t)+vapill(t,j)+dwpill(t,j);
tcost("capmnpcube",j,t)     =c2("capmnpcube",j,t)+c3("capmnpcube2",j,t)+vapill(t,j)+mnppill(t,j);
tcost("mnpdwcube",j,t)      =c2("mnpdwcube",j,t)+c3("mnpdwcube2",j,t)+dwpill(t,j)+mnppill(t,j);
*tcost("capmnpcube",j,t)     =c2("capmnpcube2",j,t)+c3("capmnpcube2",j,t)+vapill(t,j);
tcost("capmnpoil",j,t)      =c("capmnpoil",j,t)+vapill(t,j)+mnppill(t,j);
tcost("dwmnpoil",j,t)       =c("dwmnpoil",j,t)+dwpill(t,j)+mnppill(t,j);
tcost("dwmnpmaize",j,t)     =cmaize("maize",j,t)+c("dwmnp",j,t)+dwpill(t,j)+mnppill(t,j);
tcost("capmnpmaize",j,t)    =cmaize("maize",j,t)+c("capmnp",j,t)+vapill(t,j)+mnppill(t,j);
tcost("capoilmaize",j,t)    =cmaize("maize",j,t)+c("capoil",j,t)+vapill(t,j);
tcost("dwoilmaize",j,t)     =cmaize("maize",j,t)+c("dwoil",j,t)+dwpill(t,j);
tcost("oilmnpmaize",j,t)    =cmaize("maize",j,t)+c("mnpoil",j,t)+mnppill(t,j);
tcost("capcubemaize",j,t)   =cmaize("maize",j,t)+c2("capcube",j,t)+c3("capcube2",j,t)+vapill(t,j);
tcost("dwcubemaize",j,t)    =cmaize("maize",j,t)+c2("dwcube",j,t)+c3("dwcube2",j,t)+dwpill(t,j);
tcost("cubemnpmaize",j,t)   =cmaize("maize",j,t)+c2("mnpcube",j,t)+c3("mnpcube2",j,t)+mnppill(t,j);
tcost("oilcubecdti",j,t)    =ccdti("cdti",j,t)+c2("oilcube",j,t)+c3("oilcube2",j,t);
tcost("oilmaizecdti",j,t)   =ccdti("cdti",j,t)+cmaize("maize",j,t)+c("fortoil",j,t);
tcost("cubemaizecdti",j,t)  =ccdti("cdti",j,t)+cmaize("maize",j,t)+c2("fortcube",j,t)+c3("fortcube2",j,t);
tcost("oilcubehf",j,t)      =chf("hf",j,t)+c2("oilcube",j,t)+c3("oilcube2",j,t);
tcost("oilmaizehf",j,t)     =chf("hf",j,t)+cmaize("maize",j,t)+c("fortoil",j,t);
tcost("cubemaizehf",j,t)    =chf("hf",j,t)+cmaize("maize",j,t)+c2("fortcube",j,t)+c3("fortcube2",j,t);
tcost("oilcubebcc",j,t)     =c2("oilcubebcc",j,t)+c3("oilcubebcc2",j,t)+vapill(t,j);
tcost("oilmaizebcc",j,t)    =cmaize("maize",j,t)+c("oilbcc",j,t)+vapill(t,j);
tcost("cubemaizebcc",j,t)   =cmaize("maize",j,t)+c2("cubebcc",j,t)+c3("cubebcc2",j,t)+vapill(t,j);


tcost("capdwoilcube",j,t)  =c2("capdwoilcube",j,t)+c3("capdwoilcube2",j,t)+vapill(t,j)+dwpill(t,j);
tcost("capmnpoilcube",j,t) =c2("capmnpoilcube",j,t)+c3("capmnpoilcube2",j,t)+vapill(t,j)+mnppill(t,j);
tcost("dwmnpoilcube",j,t)  =c2("dwmnpoilcube",j,t)+c3("dwmnpoilcube2",j,t)+dwpill(t,j)+mnppill(t,j);
tcost("capdwoilmaize",j,t)=cmaize("maize",j,t)+c("capdwoil",j,t)+vapill(t,j)+dwpill(t,j);
tcost("capoilmnpmaize",j,t) =cmaize("maize",j,t)+c("capmnpoil",j,t)+vapill(t,j)+mnppill(t,j);
tcost("dwoilmnpmaize",j,t)  =cmaize("maize",j,t)+c("dwmnpoil",j,t)+dwpill(t,j)+mnppill(t,j);
tcost("capdwcubemaize",j,t)=cmaize("maize",j,t)+c2("capdwcube",j,t)+c3("capdwcube2",j,t)+vapill(t,j)+dwpill(t,j);
tcost("capcubemnpmaize",j,t) =cmaize("maize",j,t)+c2("capmnpcube",j,t)+c3("capmnpcube2",j,t)+vapill(t,j)+mnppill(t,j);
tcost("dwcubemnpmaize",j,t)  =cmaize("maize",j,t)+c2("mnpdwcube",j,t)+c3("mnpdwcube2",j,t)+dwpill(t,j)+mnppill(t,j);
tcost("capdwmnpoil",j,t)   =c("capdwmnpoil",j,t)+vapill(t,j)+dwpill(t,j)+mnppill(t,j);
tcost("capdwmnpcube",j,t) =c2("capdwmnpcube2",j,t)+c3("capdwmnpcube2",j,t)+vapill(t,j)+dwpill(t,j)+mnppill(t,j);
tcost("capdwmnpmaize",j,t) =cmaize("maize",j,t)+c("capdwmnp",j,t)+vapill(t,j)+dwpill(t,j)+mnppill(t,j);
tcost("capoilcubemaize",j,t)  =cmaize("maize",j,t)+c2("capoilcube",j,t)+c3("capoilcube2",j,t)+vapill(t,j);
tcost("dwoilcubemaize",j,t)  =cmaize("maize",j,t)+c2("dwoilcube",j,t)+c3("dwoilcube2",j,t)+dwpill(t,j);
tcost("oilcubemnpmaize",j,t)  =cmaize("maize",j,t)+c2("mnpoilcube",j,t)+c3("mnpoilcube2",j,t)+mnppill(t,j);
tcost("oilcubemaizecdti",j,t) =ccdti("cdti",j,t)+cmaize("maize",j,t)+c2("oilcube",j,t)+c3("oilcube2",j,t);
tcost("oilcubemaizehf",j,t)   =chf("hf",j,t)+cmaize("maize",j,t)+c2("oilcube",j,t)+c3("oilcube2",j,t);
tcost("oilcubemaizebcc",j,t)  =cmaize("maize",j,t)+c2("oilcubebcc",j,t)+c3("oilcubebcc2",j,t)+vapill(t,j);

tcost("capdwmnpoilcube",j,t)=c2("capdwmnpoilcube",j,t)+c3("capdwmnpoilcube2",j,t)+vapill(t,j)+dwpill(t,j)+mnppill(t,j);
tcost("capdwoilmnpmaize",j,t)=cmaize("maize",j,t)+c("capdwmnpoil",j,t)+vapill(t,j)+dwpill(t,j)+mnppill(t,j);
tcost("capdwcubemnpmaize",j,t)=cmaize("maize",j,t)+c2("capdwmnpcube",j,t)+c3("capdwmnpcube2",j,t)+vapill(t,j)+dwpill(t,j)+mnppill(t,j);
tcost("capdwoilcubemaize",j,t)=cmaize("maize",j,t)+c2("capdwoilcube",j,t)+c3("capdwoilcube2",j,t)+vapill(t,j)+dwpill(t,j);
tcost("capoilcubemnpmaize",j,t)=cmaize("maize",j,t)+c2("capmnpoilcube",j,t)+c3("capmnpoilcube2",j,t)+vapill(t,j)+mnppill(t,j);
tcost("dwoilcubemnpmaize",j,t)=cmaize("maize",j,t)+c2("dwmnpoilcube",j,t)+c3("dwmnpoilcube2",j,t)+dwpill(t,j)+mnppill(t,j);

tcost("capdwoilcubemnpmaize",j,t)=cmaize("maize",j,t)+c2("capdwmnpoilcube",j,t)+c3("capdwmnpoilcube2",j,t)+vapill(t,j)+dwpill(t,j)+mnppill(t,j);

* These are all the mixed combinations costs (subnational with national) for Zinc
tcostzinc("suppflour",j,t)           =czinc("suppflour",j,t)+zincpill(t,j);
tcostzinc("suppcube",j,t)            =czinc2("suppcube",j,t)+czinc3("suppcube2",j,t)+zincpill(t,j);
tcostzinc("mnpflour",j,t)            =czinc("mnpflour",j,t)+mnppill(t,j);
tcostzinc("mnpcube",j,t)             =czinc2("mnpcube",j,t)+czinc3("mnpcube2",j,t)+mnppill(t,j);
tcostzinc("mnpsuppflour",j,t)        =czinc("mnpsuppflour",j,t)+mnppill(t,j)+zincpill(t,j);
tcostzinc("mnpsuppcube",j,t)         =czinc2("mnpsuppcube",j,t)+czinc3("mnpsuppcube2",j,t)+mnppill(t,j)+zincpill(t,j);
tcostzinc("mnpflourcube",j,t)        =czinc2("mnpflourcube",j,t)+czinc3("mnpflourcube2",j,t)+mnppill(t,j);
tcostzinc("suppflourcube",j,t)       =czinc2("suppflourcube",j,t)+czinc3("suppflourcube2",j,t)+zincpill(t,j);
tcostzinc("mnpsuppflourcube",j,t)    =czinc2("mnpsuppflourcube",j,t)+czinc3("mnpsuppflourcube2",j,t)+mnppill(t,j)+zincpill(t,j);

* These are all the mixed combinations costs (subnational with national) for Iron
tcostiron("mnpflour",j,t)            =ciron("mnpflour",j,t)+mnppill(t,j);
tcostiron("mnpcube",j,t)             =ciron2("mnpcube",j,t)+ciron3("mnpcube2",j,t)+mnppill(t,j);
tcostiron("mnpflourcube",j,t)        =ciron2("mnpflourcube",j,t)+ciron3("mnpflourcube2",j,t)+mnppill(t,j);

* These are all the mixed combinations costs (subnational with national) for Folate
tcostfolate("mnpflour",j,t)          =cfolate("mnpflour",j,t)+mnppill(t,j);

* These are all the mixed combinations costs (subnational with national) for B12
tcostb12("mnpflour",j,t)             =cb12("mnpflour",j,t)+mnppill(t,j);

* These are all the mixed combinations cov (subnational with national) for VA
tcov("capoil",j,t)               =cov("capoil",j,t);
tcov("capcube",j,t)              =cov2("capsules",j,t)+cov3("capcube",j,t);
tcov("capmaize",j,t)             =cov2("capsules",j,t)+cov3("capmaize",j,t);
tcov("dwoil",j,t)                =cov("dwoil",j,t);
tcov("dwcube",j,t)               =cov2("deworming",j,t)+cov3("dwcube",j,t);
tcov("dwmaize",j,t)              =cov2("deworming",j,t)+cov3("dwmaize",j,t);
tcov("mnpoil",j,t)               =cov("mnpoil",j,t);
tcov("mnpcube",j,t)              =cov2("mnp",j,t)+cov3("mnpcube",j,t);
tcov("mnpmaize",j,t)             =cov2("mnp",j,t)+cov3("mnpmaize",j,t);
tcov("oilcdti",j,t)              =cov("oilcdti",j,t);
tcov("cubecdti",j,t)             =cov2("cdti",j,t)+cov3("cubecdti",j,t);
tcov("maizecdti",j,t)            =cov2("cdti",j,t)+cov3("maizecdti",j,t);
tcov("cubehf",j,t)             =cov2("hf",j,t)+cov3("cubehf",j,t);
tcov("maizehf",j,t)            =cov2("hf",j,t)+cov3("maizehf",j,t);
tcov("oilbcc",j,t)               =cov("oilbcc",j,t);
tcov("cubebcc",j,t)              =cov2("bcc",j,t)+cov3("cubebcc",j,t);
tcov("maizebcc",j,t)             =cov2("bcc",j,t)+cov3("maizebcc",j,t);

tcov("capoilcube",j,t)      =cov2("capoil",j,t)+cov3("capoilcube",j,t);
tcov("dwoilcube",j,t)       =cov2("dwoil",j,t)+cov3("dwoilcube",j,t);
tcov("mnpoilcube",j,t)      =cov2("mnpoil",j,t)+cov3("mnpoilcube",j,t);
tcov("capdwcube",j,t)       =cov2("capdw",j,t)+cov3("capdwcube",j,t);
tcov("capdwoil",j,t)        =cov("capdwoil",j,t);
tcov("capdwmaize",j,t)      =cov2("capdw",j,t)+cov3("capdwmaize",j,t);
tcov("capmnpcube",j,t)      =cov2("capmnp",j,t)+cov3("capmnpcube",j,t);
tcov("capmnpoil",j,t)       =cov("capmnpoil",j,t);
tcov("dwmnpoil",j,t)        =cov("dwmnpoil",j,t);
tcov("capmnpmaize",j,t)     =cov2("capmnp",j,t)+cov3("capmnpmaize",j,t);
tcov("capoilmaize",j,t)     =cov2("capoil",j,t)+cov3("capoilmaize",j,t);
tcov("dwoilmaize",j,t)      =cov2("dwoil",j,t)+cov3("dwoilmaize",j,t);
tcov("oilmnpmaize",j,t)     =cov2("mnpoil",j,t)+cov3("oilmnpmaize",j,t);
tcov("capcubemaize",j,t)    =cov2("capsules",j,t)+cov3("capcubemaize",j,t);
tcov("dwcubemaize",j,t)     =cov2("deworming",j,t)+cov3("dwcubemaize",j,t);
tcov("cubemnpmaize",j,t)    =cov2("mnp",j,t)+cov3("cubemnpmaize",j,t);
tcov("oilcubecdti",j,t)     =cov2("oilcdti",j,t)+cov3("oilcubecdti",j,t);
tcov("oilmaizecdti",j,t)    =cov2("oilcdti",j,t)+cov3("oilmaizecdti",j,t);
tcov("cubemaizecdti",j,t)   =cov2("cdti",j,t)+cov3("cubemaizecdti",j,t);
tcov("oilcubehf",j,t)       =cov2("oilhf",j,t)+cov3("oilcubehf",j,t);
tcov("oilmaizehf",j,t)      =cov2("oilhf",j,t)+cov3("oilmaizehf",j,t);
tcov("cubemaizehf",j,t)     =cov2("hf",j,t)+cov3("cubemaizehf",j,t);
tcov("oilcubebcc",j,t)     =cov2("oilbcc",j,t)+cov3("oilcubebcc",j,t);
tcov("oilmaizebcc",j,t)    =cov2("oilbcc",j,t)+cov3("oilmaizebcc",j,t);
tcov("cubemaizebcc",j,t)   =cov2("bcc",j,t)+cov3("cubemaizebcc",j,t);


tcov("capdwmnpmaize",j,t)        =cov2("capdwmnp",j,t)+cov3("capdwmnpmaize",j,t);
tcov("capdwmnpoil",j,t)          =cov("capdwmnpoil",j,t);
tcov("capdwmnpcube",j,t)         =cov2("capdwmnp",j,t)+cov3("capdwmnpcube",j,t);
tcov("capdwoilcube",j,t)         =cov2("capdwoil",j,t)+cov3("capdwoilcube",j,t);
tcov("capmnpoilcube",j,t)        =cov2("capmnpoil",j,t)+cov3("capmnpoilcube",j,t);
tcov("dwmnpoilcube",j,t)         =cov2("dwmnpoil",j,t)+cov3("dwmnpoilcube",j,t);
tcov("capdwoilmaize",j,t)        =cov2("capdwoil",j,t)+cov3("capdwoilmaize",j,t);
tcov("capoilmnpmaize",j,t)       =cov2("capmnpoil",j,t)+cov3("capoilmnpmaize",j,t);
tcov("dwoilmnpmaize",j,t)        =cov2("dwmnpoil",j,t)+cov3("dwoilmnpmaize",j,t);
tcov("capdwcubemaize",j,t)       =cov2("capdw",j,t)+cov3("capdwcubemaize",j,t);
tcov("capcubemnpmaize",j,t)      =cov2("capmnp",j,t)+cov3("capcubemnpmaize",j,t);
tcov("dwcubemnpmaize",j,t)       =cov2("dwmnp",j,t)+cov3("dwcubemnpmaize",j,t);
tcov("capoilcubemaize",j,t)      =cov2("capoil",j,t)+cov3("capoilcubemaize",j,t);
tcov("dwoilcubemaize",j,t)       =cov2("dwoil",j,t)+cov3("dwoilcubemaize",j,t);
tcov("oilcubemnpmaize",j,t)      =cov2("mnpoil",j,t)+cov3("oilcubemnpmaize",j,t);
tcov("oilcubemaizecdti",j,t)     =cov2("oilcdti",j,t)+cov3("oilcubemaizecdti",j,t);
tcov("oilcubemaizehf",j,t)       =cov2("oilhf",j,t)+cov3("oilcubemaizehf",j,t);
tcov("oilcubemaizebcc",j,t)      =cov2("oilbcc",j,t)+cov3("oilcubemaizebcc",j,t);

tcov("capdwmnpoilcube",j,t)=cov2("capdwmnpoil",j,t)+cov3("capdwmnpoilcube",j,t);
tcov("capdwcubemnpmaize",j,t)=cov2("capdwmnp",j,t)+cov3("capdwcubemnpmaize",j,t);
tcov("capdwoilmnpmaize",j,t)=cov2("capdwmnpoil",j,t)+cov3("capdwoilmnpmaize",j,t);
tcov("capdwoilcubemaize",j,t)=cov2("capdwoil",j,t)+cov3("capdwoilcubemaize",j,t);
tcov("capoilcubemnpmaize",j,t)=cov2("capmnpoil",j,t)+cov3("capoilcubemnpmaize",j,t);
tcov("dwoilcubemnpmaize",j,t)=cov2("dwmnpoil",j,t)+cov3("dwoilcubemnpmaize",j,t);

tcov("capdwoilcubemnpmaize",j,t)=cov2("capdwmnpoil",j,t)+cov3("capdwoilcubemnpmaize",j,t);

* These are all the mixed combinations cov (subnational with national) for zinc

tcovzinc("suppflour",j,t)            =covzinc("suppflour",j,t);
tcovzinc("suppcube",j,t)             =covzinc2("supp",j,t)+covzinc3("suppcube",j,t);
tcovzinc("mnpflour",j,t)             =covzinc("mnpflour",j,t);
tcovzinc("mnpcube",j,t)              =covzinc2("mnp",j,t)+covzinc3("mnpcube",j,t);
tcovzinc("mnpsuppflour",j,t)         =covzinc("mnpsuppflour",j,t);
tcovzinc("mnpsuppcube",j,t)          =covzinc2("mnpsupp",j,t)+covzinc3("mnpsuppcube",j,t);
tcovzinc("mnpflourcube",j,t)         =covzinc2("mnpflour",j,t)+covzinc3("mnpflourcube",j,t);
tcovzinc("suppflourcube",j,t)        =covzinc2("suppflour",j,t)+covzinc3("suppflourcube",j,t);
tcovzinc("mnpsuppflourcube",j,t)     =covzinc2("mnpsuppflour",j,t)+covzinc3("mnpsuppflourcube",j,t);

* These are all the mixed combinations cov (subnational with national) for iron
tcoviron("mnpflour",j,t)             =coviron("mnpflour",j,t);
tcoviron("mnpcube",j,t)              =coviron2("mnp",j,t)+coviron3("mnpcube",j,t);
tcoviron("mnpflourcube",j,t)         =coviron2("mnpflour",j,t)+coviron3("mnpflourcube",j,t);

* These are all the mixed combinations cov (subnational with national) for folate
tcovfolate("mnpflour",j,t)             =covfolate("mnpflour",j,t);

* These are all the mixed combinations cov (subnational with national) for b12
tcovb12("mnpflour",j,t)                =covb12("mnpflour",j,t);


*List Results when we have flour, cube and flourcube
tcovnone(k,j,t)=tcov(k,j,t) ;

*Reset cov to folate flour combinations instead of cube
*cov(k,j,t)=deathsaverted2(j,t,k) ;
*cov2(k,j,t2)=deathsaverted2(j,t2,k) ;
*cov3(k,j,t3)=deathsaverted2(j,t3,k) ;

* cov - subnational - VA
tcov("capsules",j,t)  =cov("capsules",j,t);
tcov("deworming",j,t) =cov("deworming",j,t);
tcov("mnp",j,t)       =cov("mnp",j,t);
tcov("capdw",j,t)     =cov("capdw",j,t);
tcov("capMNP",j,t)    =cov("capmnp",j,t);
tcov("dwmnp",j,t)     =cov("dwmnp",j,t);
tcov("capdwmnp",j,t)  =cov("capdwmnp",j,t);
tcov("cdti",j,t)      =cov("cdti",j,t);
tcov("bcc",j,t)       =cov("bcc",j,t);

* cov - national - VA
tcov("fortoil",j,t)      =cov("fortoil",j,t);
tcov("fortcube",j,t)     =cov3("fortcube",j,t);
tcov("maize",j,t)        =cov3("maize",j,t);
tcov("oilcube",j,t)      =cov2("fortoil",j,t)+cov3("oilcube",j,t);
tcov("oilmaize",j,t)     =cov2("fortoil",j,t)+cov3("oilmaize",j,t);
tcov("cubemaize",j,t)    =cov3("cubemaize",j,t);
tcov("oilcubemaize",j,t) =cov2("fortoil",j,t)+cov3("oilcubemaize",j,t);

* These are all the mixed combinations cov (subnational with national) for VA
tcov("capoil",j,t)               =cov("capoil",j,t);
tcov("capcube",j,t)              =cov2("capsules",j,t)+cov3("capcube",j,t);
tcov("capmaize",j,t)             =cov2("capsules",j,t)+cov3("capmaize",j,t);
tcov("dwoil",j,t)                =cov("dwoil",j,t);
tcov("dwcube",j,t)               =cov2("deworming",j,t)+cov3("dwcube",j,t);
tcov("dwmaize",j,t)              =cov2("deworming",j,t)+cov3("dwmaize",j,t);
tcov("mnpoil",j,t)               =cov("mnpoil",j,t);
tcov("mnpcube",j,t)              =cov2("mnp",j,t)+cov3("mnpcube",j,t);
tcov("mnpmaize",j,t)             =cov2("mnp",j,t)+cov3("mnpmaize",j,t);
tcov("oilcdti",j,t)              =cov("oilcdti",j,t);
tcov("cubecdti",j,t)             =cov2("cdti",j,t)+cov3("cubecdti",j,t);
tcov("maizecdti",j,t)            =cov2("cdti",j,t)+cov3("maizecdti",j,t);
tcov("cubehf",j,t)               =cov2("hf",j,t)+cov3("cubehf",j,t);
tcov("maizehf",j,t)              =cov2("hf",j,t)+cov3("maizehf",j,t);
tcov("oilbcc",j,t)               =cov("oilbcc",j,t);
tcov("cubebcc",j,t)              =cov2("bcc",j,t)+cov3("cubebcc",j,t);
tcov("maizebcc",j,t)             =cov2("bcc",j,t)+cov3("maizebcc",j,t);

tcov("capoilcube",j,t)      =cov2("capoil",j,t)+cov3("capoilcube",j,t);
tcov("dwoilcube",j,t)       =cov2("dwoil",j,t)+cov3("dwoilcube",j,t);
tcov("mnpoilcube",j,t)      =cov2("mnpoil",j,t)+cov3("mnpoilcube",j,t);
tcov("capdwcube",j,t)       =cov2("capdw",j,t)+cov3("capdwcube",j,t);
tcov("capdwoil",j,t)        =cov("capdwoil",j,t);
tcov("capdwmaize",j,t)      =cov2("capdw",j,t)+cov3("capdwmaize",j,t);
tcov("capmnpcube",j,t)      =cov2("capmnp",j,t)+cov3("capmnpcube",j,t);
tcov("capmnpoil",j,t)       =cov("capmnpoil",j,t);
tcov("dwmnpoil",j,t)        =cov("dwmnpoil",j,t);
tcov("capmnpmaize",j,t)     =cov2("capmnp",j,t)+cov3("capmnpmaize",j,t);
tcov("capoilmaize",j,t)     =cov2("capoil",j,t)+cov3("capoilmaize",j,t);
tcov("dwoilmaize",j,t)      =cov2("dwoil",j,t)+cov3("dwoilmaize",j,t);
tcov("oilmnpmaize",j,t)     =cov2("mnpoil",j,t)+cov3("oilmnpmaize",j,t);
tcov("capcubemaize",j,t)    =cov2("capsules",j,t)+cov3("capcubemaize",j,t);
tcov("dwcubemaize",j,t)     =cov2("deworming",j,t)+cov3("dwcubemaize",j,t);
tcov("cubemnpmaize",j,t)    =cov2("mnp",j,t)+cov3("cubemnpmaize",j,t);
tcov("oilcubecdti",j,t)     =cov2("oilcdti",j,t)+cov3("oilcubecdti",j,t);
tcov("oilmaizecdti",j,t)    =cov2("oilcdti",j,t)+cov3("oilmaizecdti",j,t);
tcov("cubemaizecdti",j,t)   =cov2("cdti",j,t)+cov3("cubemaizecdti",j,t);
tcov("oilcubehf",j,t)       =cov2("oilhf",j,t)+cov3("oilcubehf",j,t);
tcov("oilmaizehf",j,t)      =cov2("oilhf",j,t)+cov3("oilmaizehf",j,t);
tcov("cubemaizehf",j,t)     =cov2("hf",j,t)+cov3("cubemaizehf",j,t);
tcov("oilcubebcc",j,t)     =cov2("oilbcc",j,t)+cov3("oilcubebcc",j,t);
tcov("oilmaizebcc",j,t)    =cov2("oilbcc",j,t)+cov3("oilmaizebcc",j,t);
tcov("cubemaizebcc",j,t)   =cov2("bcc",j,t)+cov3("cubemaizebcc",j,t);


tcov("capdwmnpmaize",j,t)        =cov2("capdwmnp",j,t)+cov3("capdwmnpmaize",j,t);
tcov("capdwmnpoil",j,t)          =cov("capdwmnpoil",j,t);
tcov("capdwmnpcube",j,t)         =cov2("capdwmnp",j,t)+cov3("capdwmnpcube",j,t);
tcov("capdwoilcube",j,t)         =cov2("capdwoil",j,t)+cov3("capdwoilcube",j,t);
tcov("capmnpoilcube",j,t)        =cov2("capmnpoil",j,t)+cov3("capmnpoilcube",j,t);
tcov("dwmnpoilcube",j,t)         =cov2("dwmnpoil",j,t)+cov3("dwmnpoilcube",j,t);
tcov("capdwoilmaize",j,t)        =cov2("capdwoil",j,t)+cov3("capdwoilmaize",j,t);
tcov("capoilmnpmaize",j,t)       =cov2("capmnpoil",j,t)+cov3("capoilmnpmaize",j,t);
tcov("dwoilmnpmaize",j,t)        =cov2("dwmnpoil",j,t)+cov3("dwoilmnpmaize",j,t);
tcov("capdwcubemaize",j,t)       =cov2("capdw",j,t)+cov3("capdwcubemaize",j,t);
tcov("capcubemnpmaize",j,t)      =cov2("capmnp",j,t)+cov3("capcubemnpmaize",j,t);
tcov("dwcubemnpmaize",j,t)       =cov2("dwmnp",j,t)+cov3("dwcubemnpmaize",j,t);
tcov("capoilcubemaize",j,t)      =cov2("capoil",j,t)+cov3("capoilcubemaize",j,t);
tcov("dwoilcubemaize",j,t)       =cov2("dwoil",j,t)+cov3("dwoilcubemaize",j,t);
tcov("oilcubemnpmaize",j,t)      =cov2("mnpoil",j,t)+cov3("oilcubemnpmaize",j,t);
tcov("oilcubemaizecdti",j,t)     =cov2("oilcdti",j,t)+cov3("oilcubemaizecdti",j,t);
tcov("oilcubemaizehf",j,t)       =cov2("oilhf",j,t)+cov3("oilcubemaizehf",j,t);
tcov("oilcubemaizebcc",j,t)      =cov2("oilbcc",j,t)+cov3("oilcubemaizebcc",j,t);

tcov("capdwmnpoilcube",j,t)=cov2("capdwmnpoil",j,t)+cov3("capdwmnpoilcube",j,t);
tcov("capdwcubemnpmaize",j,t)=cov2("capdwmnp",j,t)+cov3("capdwcubemnpmaize",j,t);
tcov("capdwoilmnpmaize",j,t)=cov2("capdwmnpoil",j,t)+cov3("capdwoilmnpmaize",j,t);
tcov("capdwoilcubemaize",j,t)=cov2("capdwoil",j,t)+cov3("capdwoilcubemaize",j,t);
tcov("capoilcubemnpmaize",j,t)=cov2("capmnpoil",j,t)+cov3("capoilcubemnpmaize",j,t);
tcov("dwoilcubemnpmaize",j,t)=cov2("dwmnpoil",j,t)+cov3("dwoilcubemnpmaize",j,t);

tcov("capdwoilcubemnpmaize",j,t)=cov2("capdwmnpoil",j,t)+cov3("capdwoilcubemnpmaize",j,t);

*List Results when we have flour, cube and flourcube
*tcovflour(k,j,t)=tcov(k,j,t) ;

*Reset cov to folate flour combinations instead of cube
*cov(k,j,t)=deathsaverted3(j,t,k) ;
*cov2(k,j,t2)=deathsaverted3(j,t2,k) ;
*cov3(k,j,t3)=deathsaverted3(j,t3,k) ;

* cov - subnational - VA
tcov("capsules",j,t)  =cov("capsules",j,t);
tcov("deworming",j,t) =cov("deworming",j,t);
tcov("mnp",j,t)       =cov("mnp",j,t);
tcov("capdw",j,t)     =cov("capdw",j,t);
tcov("capMNP",j,t)    =cov("capmnp",j,t);
tcov("dwmnp",j,t)     =cov("dwmnp",j,t);
tcov("capdwmnp",j,t)  =cov("capdwmnp",j,t);
tcov("cdti",j,t)      =cov("cdti",j,t);
tcov("bcc",j,t)       =cov("bcc",j,t);

* cov - national - VA
tcov("fortoil",j,t)      =cov("fortoil",j,t);
tcov("fortcube",j,t)     =cov3("fortcube",j,t);
tcov("maize",j,t)        =cov3("maize",j,t);
tcov("oilcube",j,t)      =cov2("fortoil",j,t)+cov3("oilcube",j,t);
tcov("oilmaize",j,t)     =cov2("fortoil",j,t)+cov3("oilmaize",j,t);
tcov("cubemaize",j,t)    =cov3("cubemaize",j,t);
tcov("oilcubemaize",j,t) =cov2("fortoil",j,t)+cov3("oilcubemaize",j,t);

* These are all the mixed combinations cov (subnational with national) for VA
tcov("capoil",j,t)               =cov("capoil",j,t);
tcov("capcube",j,t)              =cov2("capsules",j,t)+cov3("capcube",j,t);
tcov("capmaize",j,t)             =cov2("capsules",j,t)+cov3("capmaize",j,t);
tcov("dwoil",j,t)                =cov("dwoil",j,t);
tcov("dwcube",j,t)               =cov2("deworming",j,t)+cov3("dwcube",j,t);
tcov("dwmaize",j,t)              =cov2("deworming",j,t)+cov3("dwmaize",j,t);
tcov("mnpoil",j,t)               =cov("mnpoil",j,t);
tcov("mnpcube",j,t)              =cov2("mnp",j,t)+cov3("mnpcube",j,t);
tcov("mnpmaize",j,t)             =cov2("mnp",j,t)+cov3("mnpmaize",j,t);
tcov("oilcdti",j,t)              =cov("oilcdti",j,t);
tcov("cubecdti",j,t)             =cov2("cdti",j,t)+cov3("cubecdti",j,t);
tcov("maizecdti",j,t)            =cov2("cdti",j,t)+cov3("maizecdti",j,t);
tcov("cubehf",j,t)               =cov2("hf",j,t)+cov3("cubehf",j,t);
tcov("maizehf",j,t)              =cov2("hf",j,t)+cov3("maizehf",j,t);
tcov("oilbcc",j,t)               =cov("oilbcc",j,t);
tcov("cubebcc",j,t)              =cov2("bcc",j,t)+cov3("cubebcc",j,t);
tcov("maizebcc",j,t)             =cov2("bcc",j,t)+cov3("maizebcc",j,t);

tcov("capoilcube",j,t)      =cov2("capoil",j,t)+cov3("capoilcube",j,t);
tcov("dwoilcube",j,t)       =cov2("dwoil",j,t)+cov3("dwoilcube",j,t);
tcov("mnpoilcube",j,t)      =cov2("mnpoil",j,t)+cov3("mnpoilcube",j,t);
tcov("capdwcube",j,t)       =cov2("capdw",j,t)+cov3("capdwcube",j,t);
tcov("capdwoil",j,t)        =cov("capdwoil",j,t);
tcov("capdwmaize",j,t)      =cov2("capdw",j,t)+cov3("capdwmaize",j,t);
tcov("capmnpcube",j,t)      =cov2("capmnp",j,t)+cov3("capmnpcube",j,t);
tcov("capmnpoil",j,t)       =cov("capmnpoil",j,t);
tcov("dwmnpoil",j,t)        =cov("dwmnpoil",j,t);
tcov("capmnpmaize",j,t)     =cov2("capmnp",j,t)+cov3("capmnpmaize",j,t);
tcov("capoilmaize",j,t)     =cov2("capoil",j,t)+cov3("capoilmaize",j,t);
tcov("dwoilmaize",j,t)      =cov2("dwoil",j,t)+cov3("dwoilmaize",j,t);
tcov("oilmnpmaize",j,t)     =cov2("mnpoil",j,t)+cov3("oilmnpmaize",j,t);
tcov("capcubemaize",j,t)    =cov2("capsules",j,t)+cov3("capcubemaize",j,t);
tcov("dwcubemaize",j,t)     =cov2("deworming",j,t)+cov3("dwcubemaize",j,t);
tcov("cubemnpmaize",j,t)    =cov2("mnp",j,t)+cov3("cubemnpmaize",j,t);
tcov("oilcubecdti",j,t)     =cov2("oilcdti",j,t)+cov3("oilcubecdti",j,t);
tcov("oilmaizecdti",j,t)    =cov2("oilcdti",j,t)+cov3("oilmaizecdti",j,t);
tcov("cubemaizecdti",j,t)   =cov2("cdti",j,t)+cov3("cubemaizecdti",j,t);
tcov("oilcubehf",j,t)       =cov2("oilhf",j,t)+cov3("oilcubehf",j,t);
tcov("oilmaizehf",j,t)      =cov2("oilhf",j,t)+cov3("oilmaizehf",j,t);
tcov("cubemaizehf",j,t)     =cov2("hf",j,t)+cov3("cubemaizehf",j,t);
tcov("oilcubebcc",j,t)     =cov2("oilbcc",j,t)+cov3("oilcubebcc",j,t);
tcov("oilmaizebcc",j,t)    =cov2("oilbcc",j,t)+cov3("oilmaizebcc",j,t);
tcov("cubemaizebcc",j,t)   =cov2("bcc",j,t)+cov3("cubemaizebcc",j,t);


tcov("capdwmnpmaize",j,t)        =cov2("capdwmnp",j,t)+cov3("capdwmnpmaize",j,t);
tcov("capdwmnpoil",j,t)          =cov("capdwmnpoil",j,t);
tcov("capdwmnpcube",j,t)         =cov2("capdwmnp",j,t)+cov3("capdwmnpcube",j,t);
tcov("capdwoilcube",j,t)         =cov2("capdwoil",j,t)+cov3("capdwoilcube",j,t);
tcov("capmnpoilcube",j,t)        =cov2("capmnpoil",j,t)+cov3("capmnpoilcube",j,t);
tcov("dwmnpoilcube",j,t)         =cov2("dwmnpoil",j,t)+cov3("dwmnpoilcube",j,t);
tcov("capdwoilmaize",j,t)        =cov2("capdwoil",j,t)+cov3("capdwoilmaize",j,t);
tcov("capoilmnpmaize",j,t)       =cov2("capmnpoil",j,t)+cov3("capoilmnpmaize",j,t);
tcov("dwoilmnpmaize",j,t)        =cov2("dwmnpoil",j,t)+cov3("dwoilmnpmaize",j,t);
tcov("capdwcubemaize",j,t)       =cov2("capdw",j,t)+cov3("capdwcubemaize",j,t);
tcov("capcubemnpmaize",j,t)      =cov2("capmnp",j,t)+cov3("capcubemnpmaize",j,t);
tcov("dwcubemnpmaize",j,t)       =cov2("dwmnp",j,t)+cov3("dwcubemnpmaize",j,t);
tcov("capoilcubemaize",j,t)      =cov2("capoil",j,t)+cov3("capoilcubemaize",j,t);
tcov("dwoilcubemaize",j,t)       =cov2("dwoil",j,t)+cov3("dwoilcubemaize",j,t);
tcov("oilcubemnpmaize",j,t)      =cov2("mnpoil",j,t)+cov3("oilcubemnpmaize",j,t);
tcov("oilcubemaizecdti",j,t)     =cov2("oilcdti",j,t)+cov3("oilcubemaizecdti",j,t);
tcov("oilcubemaizehf",j,t)       =cov2("oilhf",j,t)+cov3("oilcubemaizehf",j,t);
tcov("oilcubemaizebcc",j,t)      =cov2("oilbcc",j,t)+cov3("oilcubemaizebcc",j,t);

tcov("capdwmnpoilcube",j,t)=cov2("capdwmnpoil",j,t)+cov3("capdwmnpoilcube",j,t);
tcov("capdwcubemnpmaize",j,t)=cov2("capdwmnp",j,t)+cov3("capdwcubemnpmaize",j,t);
tcov("capdwoilmnpmaize",j,t)=cov2("capdwmnpoil",j,t)+cov3("capdwoilmnpmaize",j,t);
tcov("capdwoilcubemaize",j,t)=cov2("capdwoil",j,t)+cov3("capdwoilcubemaize",j,t);
tcov("capoilcubemnpmaize",j,t)=cov2("capmnpoil",j,t)+cov3("capoilcubemnpmaize",j,t);
tcov("dwoilcubemnpmaize",j,t)=cov2("dwmnpoil",j,t)+cov3("dwoilcubemnpmaize",j,t);

tcov("capdwoilcubemnpmaize",j,t)=cov2("capdwmnpoil",j,t)+cov3("capdwoilcubemnpmaize",j,t);

*List Results when we have flour, cube and flourcube
*tcovflourcube(k,j,t)=tcov(k,j,t) ;

*Reset cov to no folate combinations instead of flourcube
*cov(k,j,t)=deathsaverted4(j,t,k) ;
*cov2(k,j,t2)=deathsaverted4(j,t2,k) ;
*cov3(k,j,t3)=deathsaverted4(j,t3,k) ;

* cov - subnational - VA
tcov("capsules",j,t)  =cov("capsules",j,t);
tcov("deworming",j,t) =cov("deworming",j,t);
tcov("mnp",j,t)       =cov("mnp",j,t);
tcov("capdw",j,t)     =cov("capdw",j,t);
tcov("capMNP",j,t)    =cov("capmnp",j,t);
tcov("dwmnp",j,t)     =cov("dwmnp",j,t);
tcov("capdwmnp",j,t)  =cov("capdwmnp",j,t);
tcov("cdti",j,t)      =cov("cdti",j,t);
tcov("bcc",j,t)       =cov("bcc",j,t);

* cov - national - VA
tcov("fortoil",j,t)      =cov("fortoil",j,t);
tcov("fortcube",j,t)     =cov3("fortcube",j,t);
tcov("maize",j,t)        =cov3("maize",j,t);
tcov("oilcube",j,t)      =cov2("fortoil",j,t)+cov3("oilcube",j,t);
tcov("oilmaize",j,t)     =cov2("fortoil",j,t)+cov3("oilmaize",j,t);
tcov("cubemaize",j,t)    =cov3("cubemaize",j,t);
tcov("oilcubemaize",j,t) =cov2("fortoil",j,t)+cov3("oilcubemaize",j,t);

* These are all the mixed combinations cov (subnational with national) for VA
tcov("capoil",j,t)               =cov("capoil",j,t);
tcov("capcube",j,t)              =cov2("capsules",j,t)+cov3("capcube",j,t);
tcov("capmaize",j,t)             =cov2("capsules",j,t)+cov3("capmaize",j,t);
tcov("dwoil",j,t)                =cov("dwoil",j,t);
tcov("dwcube",j,t)               =cov2("deworming",j,t)+cov3("dwcube",j,t);
tcov("dwmaize",j,t)              =cov2("deworming",j,t)+cov3("dwmaize",j,t);
tcov("mnpoil",j,t)               =cov("mnpoil",j,t);
tcov("mnpcube",j,t)              =cov2("mnp",j,t)+cov3("mnpcube",j,t);
tcov("mnpmaize",j,t)             =cov2("mnp",j,t)+cov3("mnpmaize",j,t);
tcov("oilcdti",j,t)              =cov("oilcdti",j,t);
tcov("cubecdti",j,t)             =cov2("cdti",j,t)+cov3("cubecdti",j,t);
tcov("maizecdti",j,t)            =cov2("cdti",j,t)+cov3("maizecdti",j,t);
tcov("cubehf",j,t)               =cov2("hf",j,t)+cov3("cubehf",j,t);
tcov("maizehf",j,t)              =cov2("hf",j,t)+cov3("maizehf",j,t);
tcov("oilbcc",j,t)               =cov("oilbcc",j,t);
tcov("cubebcc",j,t)              =cov2("bcc",j,t)+cov3("cubebcc",j,t);
tcov("maizebcc",j,t)             =cov2("bcc",j,t)+cov3("maizebcc",j,t);

tcov("capoilcube",j,t)      =cov2("capoil",j,t)+cov3("capoilcube",j,t);
tcov("dwoilcube",j,t)       =cov2("dwoil",j,t)+cov3("dwoilcube",j,t);
tcov("mnpoilcube",j,t)      =cov2("mnpoil",j,t)+cov3("mnpoilcube",j,t);
tcov("capdwcube",j,t)       =cov2("capdw",j,t)+cov3("capdwcube",j,t);
tcov("capdwoil",j,t)        =cov("capdwoil",j,t);
tcov("capdwmaize",j,t)      =cov2("capdw",j,t)+cov3("capdwmaize",j,t);
tcov("capmnpcube",j,t)      =cov2("capmnp",j,t)+cov3("capmnpcube",j,t);
tcov("capmnpoil",j,t)       =cov("capmnpoil",j,t);
tcov("dwmnpoil",j,t)        =cov("dwmnpoil",j,t);
tcov("capmnpmaize",j,t)     =cov2("capmnp",j,t)+cov3("capmnpmaize",j,t);
tcov("capoilmaize",j,t)     =cov2("capoil",j,t)+cov3("capoilmaize",j,t);
tcov("dwoilmaize",j,t)      =cov2("dwoil",j,t)+cov3("dwoilmaize",j,t);
tcov("oilmnpmaize",j,t)     =cov2("mnpoil",j,t)+cov3("oilmnpmaize",j,t);
tcov("capcubemaize",j,t)    =cov2("capsules",j,t)+cov3("capcubemaize",j,t);
tcov("dwcubemaize",j,t)     =cov2("deworming",j,t)+cov3("dwcubemaize",j,t);
tcov("cubemnpmaize",j,t)    =cov2("mnp",j,t)+cov3("cubemnpmaize",j,t);
tcov("oilcubecdti",j,t)     =cov2("oilcdti",j,t)+cov3("oilcubecdti",j,t);
tcov("oilmaizecdti",j,t)    =cov2("oilcdti",j,t)+cov3("oilmaizecdti",j,t);
tcov("cubemaizecdti",j,t)   =cov2("cdti",j,t)+cov3("cubemaizecdti",j,t);
tcov("oilcubehf",j,t)       =cov2("oilhf",j,t)+cov3("oilcubehf",j,t);
tcov("oilmaizehf",j,t)      =cov2("oilhf",j,t)+cov3("oilmaizehf",j,t);
tcov("cubemaizehf",j,t)     =cov2("hf",j,t)+cov3("cubemaizehf",j,t);
tcov("oilcubebcc",j,t)     =cov2("oilbcc",j,t)+cov3("oilcubebcc",j,t);
tcov("oilmaizebcc",j,t)    =cov2("oilbcc",j,t)+cov3("oilmaizebcc",j,t);
tcov("cubemaizebcc",j,t)   =cov2("bcc",j,t)+cov3("cubemaizebcc",j,t);


tcov("capdwmnpmaize",j,t)        =cov2("capdwmnp",j,t)+cov3("capdwmnpmaize",j,t);
tcov("capdwmnpoil",j,t)          =cov("capdwmnpoil",j,t);
tcov("capdwmnpcube",j,t)         =cov2("capdwmnp",j,t)+cov3("capdwmnpcube",j,t);
tcov("capdwoilcube",j,t)         =cov2("capdwoil",j,t)+cov3("capdwoilcube",j,t);
tcov("capmnpoilcube",j,t)        =cov2("capmnpoil",j,t)+cov3("capmnpoilcube",j,t);
tcov("dwmnpoilcube",j,t)         =cov2("dwmnpoil",j,t)+cov3("dwmnpoilcube",j,t);
tcov("capdwoilmaize",j,t)        =cov2("capdwoil",j,t)+cov3("capdwoilmaize",j,t);
tcov("capoilmnpmaize",j,t)       =cov2("capmnpoil",j,t)+cov3("capoilmnpmaize",j,t);
tcov("dwoilmnpmaize",j,t)        =cov2("dwmnpoil",j,t)+cov3("dwoilmnpmaize",j,t);
tcov("capdwcubemaize",j,t)       =cov2("capdw",j,t)+cov3("capdwcubemaize",j,t);
tcov("capcubemnpmaize",j,t)      =cov2("capmnp",j,t)+cov3("capcubemnpmaize",j,t);
tcov("dwcubemnpmaize",j,t)       =cov2("dwmnp",j,t)+cov3("dwcubemnpmaize",j,t);
tcov("capoilcubemaize",j,t)      =cov2("capoil",j,t)+cov3("capoilcubemaize",j,t);
tcov("dwoilcubemaize",j,t)       =cov2("dwoil",j,t)+cov3("dwoilcubemaize",j,t);
tcov("oilcubemnpmaize",j,t)      =cov2("mnpoil",j,t)+cov3("oilcubemnpmaize",j,t);
tcov("oilcubemaizecdti",j,t)     =cov2("oilcdti",j,t)+cov3("oilcubemaizecdti",j,t);
tcov("oilcubemaizehf",j,t)       =cov2("oilhf",j,t)+cov3("oilcubemaizehf",j,t);
tcov("oilcubemaizebcc",j,t)      =cov2("oilbcc",j,t)+cov3("oilcubemaizebcc",j,t);

tcov("capdwmnpoilcube",j,t)=cov2("capdwmnpoil",j,t)+cov3("capdwmnpoilcube",j,t);
tcov("capdwcubemnpmaize",j,t)=cov2("capdwmnp",j,t)+cov3("capdwcubemnpmaize",j,t);
tcov("capdwoilmnpmaize",j,t)=cov2("capdwmnpoil",j,t)+cov3("capdwoilmnpmaize",j,t);
tcov("capdwoilcubemaize",j,t)=cov2("capdwoil",j,t)+cov3("capdwoilcubemaize",j,t);
tcov("capoilcubemnpmaize",j,t)=cov2("capmnpoil",j,t)+cov3("capoilcubemnpmaize",j,t);
tcov("dwoilcubemnpmaize",j,t)=cov2("dwmnpoil",j,t)+cov3("dwoilcubemnpmaize",j,t);

tcov("capdwoilcubemnpmaize",j,t)=cov2("capdwmnpoil",j,t)+cov3("capdwoilcubemnpmaize",j,t);

*List Results when we have cube folate
*tcovcube(k,j,t)=tcov(k,j,t) ;

*tcostfolate2(k,j,t3)=tcostfolate(k,j,t3);

*display tcovcube, tcovflour, tcovflourcube, tcovnone, tcostfolate2;

* Equation for BAU* total benefits, using weights and discount factor
*BAU List
*totalbenefitsbau=sum(t,GAMMA(t)*(sum((j),tcovnone("capdwoil",j,t)+fdeathsaverted(j,t,"flour"))));


totalbenefitsbau=sum(t,GAMMA(t)*(sum((j),vawght*(alphakids*tcov("capdwoil",j,t)+betawra*tcovwra("fortoil",j,t))
                         +zincwght*(zinckidwght*tcovzinc("flour",j,t)+zincwrawght*tcovzincwra("flour",j,t))+ironwght*(ironkidwght*tcoviron("flour",j,t)+ironwrawght*tcovironwra("flour",j,t))+
                         folatewght*(folatekidwght*tcovfolate("flour",j,t)+folatewrawght*tcovfolatewra("flour",j,t))+b12wght*(b12kidwght*tcovb12("flour",j,t))+b12wght*(b12wrawght*tcovb12wra("flour",j,t)))));

totalbenefitsbau2(j)=sum(t,GAMMA(t)*(vawght*(alphakids*tcov("capdwoil",j,t)+betawra*tcovwra("fortoil",j,t))
                         +zincwght*(zinckidwght*tcovzinc("flour",j,t)+zincwrawght*tcovzincwra("flour",j,t)+b12wght*(b12wrawght*tcovb12wra("flour",j,t)))));

totalbenefitsbau3(t)=sum(j,GAMMA(t)*tcov("capoil",j,t)) ;

*totalbenefitsbau3(t)=sum(j,GAMMA(t)*(vawght*(alphakids*tcov("capdwoil",j,t)+betawra*tcovwra("fortoil",j,t))
*                         +zincwght*(zinckidwght*tcovzinc("flour",j,t)+zincwrawght*tcovzincwra("flour",j,t))+b12wght*(b12wrawght*tcovb12wra("flour",j,t))));

*totalbenefitsbau3(t)=sum(j,tcovfolatewra("flour",j,t));

totalbenefitsbau4(j,t)=GAMMA(t)*(vawght*(alphakids*tcov("capdwoil",j,t)+betawra*tcovwra("fortoil",j,t))
                         +zincwght*(zinckidwght*tcovzinc("flour",j,t)+zincwrawght*tcovzincwra("flour",j,t)));

totalbenefitsbauva=sum(t,GAMMA(t)*(sum((j),vawght*(alphakids*tcov("capdwoil",j,t)+betawra*tcovwra("fortoil",j,t)))));

totalbenefitsbauvakids=sum(t,GAMMA(t)*(sum((j),vawght*(alphakids*tcov("capdwoil",j,t)))));

totalbenefits2=percben*totalbenefitsbau ;

display totalbenefits2, totalbenefitsbau3;
***************TEST
tcosttest("fcube",k,j,t)=tcost(k,j,t)  ;
tcosttest("fflour",k,j,t)=tcost(k,j,t)+tcostfolate("flour",j,t)  ;
tcosttest("fflourcube",k,j,t)=tcost(k,j,t)+tcostfolate("flour",j,t);

tcovcube(k,j,t)=tcovnone(k,j,t) ;
tcovflour(k,j,t)=tcovnone(k,j,t) ;
tcovflourcube(k,j,t)=tcovnone(k,j,t) ;

tcovtest("fcube",k,j,t)=tcovcube(k,j,t) ;
tcovtest("fflour",k,j,t)=tcovflour(k,j,t);
tcovtest("fflourcube",k,j,t)=tcovflourcube(k,j,t);

costnew(k,j,t)   =tcost(k,j,t) ;
*Experiment - lower cost of VA overhead
costnew(capk,"north",t) = tcost(capk,"north",t)-436937.583;
costnew(capk,"south",t) = tcost(capk,"south",t)-646975.2633;
costnew(capk,"cities",t) = tcost(capk,"south",t)-258744.2649;
tcost(k,j,t) =costnew(k,j,t) ;


display costnew, tcost , tcov, tcovwra, tcostzinc, tcovzinc, tcovzincwra, tcostiron, tcoviron, tcostfolate, tcovfolate,
tcostb12, tcovb12, tcovb12wra, tcovironwra, totalbenefitsbau, totalbenefitsbau3, tcosttest, tcovtest, totalbenefits2;



* set specialk(oilk) / bla bla bla /
* tcov(oilk,j,t) = cov(oilk,j,t) + cov2(oilk,j,t)$specialk(oilk) ;

;
tcovflour(cdtik,j,t) = includecdti*tcovflour(cdtik,j,t) ;
tcovcube(cdtik,j,t) = includecdti*tcovcube(cdtik,j,t) ;
tcovflourcube(cdtik,j,t) = includecdti*tcovflourcube(cdtik,j,t) ;
tcov(cdtik,j,t) = includecdti*tcov(cdtik,j,t) ;
tcov(hfk,j,t) = includehf*tcov(hfk,j,t) ;
*tcostfolate("fortcube",j,t)=0;
*tcostfolate("flourcube",j,t)=tcostfolate("flour",j,t);
*tcost(cdtik,j,t) = tcost(cdtik,j,t)/2 ;
*tcov(maizek,j,t)=tcov(maizek,j,t)*1.04;
*tcost(maizek,j,t)=tcost(maizek,j,t)-tcost(maizek,j,t)*.2;

*tcov("capdwoilcube",j,t)=0;
tcov("capdwMNPoilcube",j,t)=0;
tcov("capMNPoilcube",j,t)=0;


Variables
X(k,j,t)      QUANTITY OF VA INTERVENTION ZErO OR ONE
Y(k,j,t)      QUANTITY OF VA INTERVENTION ZERO OR ONE
W(k,j,t)      QUANTITY OF VA INTERVENTION ZERO OR ONE
V(k,j,t)      QUANTITY OF VA INTERVENTION ZERO OR ONE
XCOST         TOTAL COST FOR X VARIABLE INTERVENTIONS
XCOV1          TOTAL COVERAGE FOR X VARIABLE INTERVENTIONS
XCOV2          TOTAL COVERAGE FOR X VARIABLE INTERVENTIONS
XCOV3          TOTAL COVERAGE FOR X VARIABLE INTERVENTIONS
XCOV4          TOTAL COVERAGE FOR X VARIABLE INTERVENTIONS
XCOV          TOTAL COVERAGE FOR X VARIABLE INTERVENTIONS
Z             TOTAL COSTS
BEN           TOTAL COVERAGE
BENFIRST3(t2) TOTAL COVERAGE IN THE FIRST 3 YEARS
BENSPACE(j)   TOTAL COVERAGE BY SPACE
BENTIME(t)    TOTAL COVERAGE BY TIME
BENSPACETIME(j,t)  TOTAL COVERAGE BY SPACE & TIME
BENVA         TOTAL COVERAGE BY SPACE & TIME FOR VA
BENVAKIDS     TOTAL COVERAGE BY SPACE & TIME FOR VA CHILDREN
YESOIL(j,t)    equal to 1 if there is oil in j at t
YESCUBE(j,t)   equal to 1 if there is cube in j at t
YESMAIZE(j,t)  equal to 1 if there is maize in j at t
YESOIL2(j,t)    equal to 1 if there is oil in j at t
YESCUBE2(j,t)   equal to 1 if there is cube in j at t
YESMAIZE2(j,t)  equal to 1 if there is maize in j at t
YESOIL3(j,t)    equal to 1 if there is oil in j at t
YESCUBE3(j,t)   equal to 1 if there is cube in j at t
YESMAIZE3(j,t)  equal to 1 if there is maize in j at t
YESOIL4(j,t)    equal to 1 if there is oil in j at t
YESCUBE4(j,t)   equal to 1 if there is cube in j at t
YESMAIZE4(j,t)  equal to 1 if there is maize in j at t
YESCAP(j,t)    equal to 1 if there is capsules in j at t
YESDW(j,t)     equal to 1 if there is unenhanced oil in j at t
YESZINCCUBE(j,t)  equal to 1 if there is zinc cube in j at t
YESFLOUR(j,t)  equal to 1 if there is flour in j at t
YESFOLATEFLOUR(j,t)  equal to 1 if there is folate flour in j at t
YESFOLATECUBE(j,t)  equal to 1 if there is folate cube in j at t
YESB12FLOUR(j,t)  equal to 1 if there is b12 flour in j at t
YESB12CUBE(j,t)  equal to 1 if there is b12 cube in j at t
YESIRONFLOUR(j,t)  equal to 1 if there is iron flour in j at t
YESIRONCUBE(j,t)  equal to 1 if there is iron cube in j at t
YESMNPX(j,t)  equal to 1 if there is MNP in j at t
YESMNPY(j,t)  equal to 1 if there is MNP in j at t
;

Binary Variable X, Y, W, V;

* this is useful to refer to two regions within a single equation
alias (j,jj) ;
alias (t,tt) ;

Equations
benefit                  TOTAL AMOUNT OF COVERAGE BENEFITS
*benefitfirst3            TOTAL AMOUNT OF PEOPLE THAT MUST BENEFIT IN THE FIRST 3 YEARS
benefitconst             TOTAL AMOUNT OF PEOPLE THAT MUST BENEFIT IN TOTAL
*benefitva                TOTAL AMOUNT OF PEOPLE THAT MUST BENEFIT FROM VA
*benefitconstva           TOTAL AMOUNT OF PEOPLE THAT MUST BENEFIT FROM VA
*benefitvakids            TOTAL AMOUNT OF CHILDREN THAT MUST BENEFIT FROM VA
*benefitconstvakids       TOTAL AMOUNT OF CHILDREN THAT MUST BENEFIT FROM VA
*benconstfirst3           TOTAL AMOUNT OF PEOPLE THAT MUST BENEFIT IN THE FIRST 3 YEARS
*Equity model space
*benefitconstspace            TOTAL AMOUNT OF PEOPLE THAT MUST BENEFIT IN TOTAL
*benefitspace(j)              TOTAL AMOUNT OF COVERAGE BENEFITS BY SPACE

*Equity model time
*benefitconsttime(t)          TOTAL AMOUNT OF PEOPLE THAT MUST BENEFIT IN TOTAL
*benefittime(t)              TOTAL AMOUNT OF COVERAGE BENEFITS BY TIME

*Equity model space/time
*benefitconstspacetime(j,t)       TOTAL AMOUNT OF PEOPLE THAT MUST BENEFIT IN TOTAL
*benefitspacetime(j,t)            TOTAL AMOUNT OF COVERAGE BENEFITS BY SPACE & TIME

*fundconst                THE TOTAL AMOUNT OF FUNDING
cost                     TOTAL COSTS FOR THE OPTIMAL INTERVENTIONS
onesx(j,t)               A CONSTRAINT ON THE NUMBER OF INTERVENTIONS THAT CAN BE CHOSEN FOR X VARIABLES INTERVENTIONS
onesy(j,t)               A CONSTRAINT ON THE NUMBER OF INTERVENTIONS THAT CAN BE CHOSEN FOR Y VARIABLES INTERVENTIONS
*onesw(j,t)               A CONSTRAINT ON THE NUMBER OF INTERVENTIONS THAT CAN BE CHOSEN FOR Y VARIABLES INTERVENTIONS
*oneswxy(j,t)               A CONSTRAINT ON THE NUMBER OF INTERVENTIONS THAT CAN BE CHOSEN FOR Y VARIABLES INTERVENTIONS
*xcoveq1(k,j,t)            THE AMOUNT OF COVERAGE FOR X
*xcoveq2(k,j,t)            THE AMOUNT OF COVERAGE FOR Y
*xcoveq3(k,j,t)            THE AMOUNT OF COVERAGE FOR W
*xcoveq4(k,j,t)            THE AMOUNT OF COVERAGE FOR V
xcoveq(k,j,t)            THE AMOUNT OF COVERAGE FOR X
xcosteq(k,j,t)           THE AMOUNT OF COST FOR X

* Equations that force national interventions to be national:
yesoileq(j,t)        equation defining yesoil>0 if there is oil in j
yescubeeq(j,t)       equation defining yescube>0 if there is cube in j
yesmaizeeq(j,t)      equation defining yescube>0 if there is maize in j
yesdweq(j,t)         equation defining yesunehancedoil>0 if there is unenhancedoil in j
yesoileq2(j,t)        equation defining yesoil>0 if there is oil in j
yescubeeq2(j,t)       equation defining yescube>0 if there is cube in j
yesmaizeeq2(j,t)      equation defining yescube>0 if there is maize in j
yesoileq3(j,t)        equation defining yesoil>0 if there is oil in j
yescubeeq3(j,t)       equation defining yescube>0 if there is cube in j
yesmaizeeq3(j,t)      equation defining yescube>0 if there is maize in j
yesoileq4(j,t)        equation defining yesoil>0 if there is oil in j
yescubeeq4(j,t)       equation defining yescube>0 if there is cube in j
yesmaizeeq4(j,t)      equation defining yescube>0 if there is maize in j
yescapeq(j,t)            equation defining yescube>0 if there is capsules in j
yeszinccubeeq(j,t)       equation defining yescube>0 if there is cube in j
yesfloureq(j,t)      equation defining yesflour>0 if there is flour in j
yesfolatefloureq(j,t)      equation defining yesflour>0 if there is folate flour in j
yesfolatecubeeq(j,t)      equation defining yesflour>0 if there is folate flour in j
yesb12floureq(j,t)      equation defining yesflour>0 if there is b12 flour in j
yesb12cubeeq(j,t)      equation defining yesflour>0 if there is b12 flour in j
yesironfloureq(j,t)      equation defining yesflour>0 if there is iron flour in j
yesironcubeeq(j,t)      equation defining yesflour>0 if there is iron flour in j
yesmnpeq(j,t)      equation defining yesmnp>0 if there is mnp in j
yesmnpeq2(j,t)      equation defining yesmnp>0 if there is mnp in j
allnooileq(j,jj,t) equation
alloileq(j,jj,t)     equation forcing oil to be either 1 or 0 in all regions
allcubeeq(j,jj,t)    equation forcing cube to be either 1 or 0 in all regions
allmaizeeq(j,jj,t)   equation forcing maize to be either 1 or 0 in all regions
alldweq(j,jj,t)      equation forcing unenhanced oil to be either 1 or 0 in all regions
alloileq2(j,jj,t)     equation forcing oil to be either 1 or 0 in all regions
allcubeeq3(j,jj,t)    equation forcing cube to be either 1 or 0 in all regions
allmaizeeq3(j,jj,t)   equation forcing maize to be either 1 or 0 in all regions
alloileq3(j,jj,t)     equation forcing oil to be either 1 or 0 in all regions
alloileq4(j,jj,t)     equation forcing oil to be either 1 or 0 in all regions
allcubeeq4(j,jj,t)    equation forcing cube to be either 1 or 0 in all regions
allmaizeeq4(j,jj,t)   equation forcing maize to be either 1 or 0 in all regions
allcubeeq5(j,jj,t)    equation forcing cube to be either 1 or 0 in all regions
allmaizeeq5(j,jj,t)   equation forcing maize to be either 1 or 0 in all regions
allzinccubeeq(j,jj,t)    equation forcing cube to be either 1 or 0 in all regions
allfloureq(j,jj,t)   equation forcing flour to be either 1 or 0 in all regions
allfolatefloureq(j,jj,t)   equation forcing folate flour to be either 1 or 0 in all regions
allfolatecubeeq(j,jj,t)   equation forcing folate cube to be either 1 or 0 in all regions
allb12floureq(j,jj,t)   equation forcing b12 flour to be either 1 or 0 in all regions
allb12cubeeq(j,jj,t)    equation forcing b12 cube to be either 1 or 0 in all regions
allironfloureq(j,jj,t)   equation forcing iron flour to be either 1 or 0 in all regions
allironcubeeq(j,jj,t)    equation forcing iron cube to be either 1 or 0 in all regions
allmnpeq(j,jj,t)   equation forcing mnp to be either 1 or 0 in all x and y
allcubeeq2(j,t2,tt)    equation forcing cube to be either 1 or 0 in all time
allzinccubeeq2(j,t2,tt)    equation forcing zinc cube to be either 1 or 0 in all time
allb12cubeeq2(j,t2,tt)    equation forcing b12 cube to be either 1 or 0 in all time
allironcubeeq2(j,t2,tt)    equation forcing iron cube to be either 1 or 0 in all time
allfolatecubeeq2(j,t2,tt)    equation forcing folate cube to be either 1 or 0 in all time
*allb12floureq2(j,t2,tt)    equation forcing flour to be either 1 or 0 in all time
allmaizeeq2(j,t2,tt)     equation forcing cube to be either 1 or 0 in all time
allmaizeeq6(j,t2,tt)     equation forcing cube to be either 1 or 0 in all time
allcubeeq6(j,t2,tt)    equation forcing cube to be either 1 or 0 in all time
allmaizeeq7(j,t2,tt)     equation forcing cube to be either 1 or 0 in all time
allcubeeq7(j,t2,tt)    equation forcing cube to be either 1 or 0 in all time
allmaizeeq8(j,t2,tt)     equation forcing cube to be either 1 or 0 in all time
allcubeeq8(j,t2,tt)    equation forcing cube to be either 1 or 0 in all time

;

*tcovflour(oilk,j,t)=tcovflour(oilk,j,t)*1.002;

* Coverage and cost:
*xcoveq1(k,j,t) ..        XCOV1(k,j,t)=e=(tcovnone(k,j,t))*x(k,j,t);
*xcoveq2(k,j,t) ..        XCOV2(k,j,t)=e=(tcovflour(k,j,t))*y(k,j,t);
*xcoveq3(k,j,t) ..        XCOV3(k,j,t)=e=(tcovflourcube(k,j,t))*w(k,j,t);
*xcoveq4(k,j,t) ..        XCOV4(k,j,t)=e=(tcovnone(k,j,t))*v(k,j,t);
*xcoveq(k,j,t)  ..        XCOV(k,j,t)=e=tcovnone(k,j,t)*x(k,j,t)+fdeathsaverted(j,t,k)*y(k,j,t);
*xcoveq(k,j,t) ..         XCOV(k,j,t)=e=XCOV1(k,j,t)+XCOV2(k,j,t)+XCOV3(k,j,t);
xcoveq(k,j,t) ..       XCOV(k,j,t)=e=vawght*(alphakids*tcov(k,j,t)+betawra*tcovwra(k,j,t))*x(k,j,t)+
                                 zincwght*(zinckidwght*tcovzinc(k,j,t)+zincwrawght*tcovzincwra(k,j,t))*y(k,j,t)+ironwght*(ironkidwght*tcoviron(k,j,t)+ironwrawght*tcovironwra(k,j,t))*x(k,j,t)
                                 +folatewght*(folatekidwght*tcovfolate(k,j,t)+folatewrawght*tcovfolatewra(k,j,t))*x(k,j,t)+b12wght*(b12kidwght*tcovb12(k,j,t)*x(k,j,t)
                                 +b12wrawght*tcovb12wra(k,j,t))*x(k,j,t);
*xcosteq(k,j,t) ..        XCOST(k,j,t)=e=tcost(k,j,t)*x(k,j,t)+tcostfolate(k,j,t)*y(k,j,t);
xcosteq(k,j,t) ..      XCOST(k,j,t)=e=vawght*tcost(k,j,t)*x(k,j,t)+zincwghtc*tcostzinc(k,j,t)*y(k,j,t)+ironwght*tcostiron(k,j,t)*x(k,j,t)
                                 +folatewght*tcostfolate(k,j,t)*x(k,j,t)+b12wght*tcostb12(k,j,t)*x(k,j,t)-vawght*zincwghtc*tcostzinc("mnp",j,t)*y(k,j,t)$mnpzinck(k);
benefit ..             BEN=e=sum(t,GAMMA(t)*(sum((k,j),XCOV(k,j,t))));
*benefitfirst3(t2) ..   BENFIRST3(t2)=e=sum(t,GAMMA(t2)*(sum((k,j),XCOV(k,j,t2))));
*benefitva ..           BENVA=e=sum(t,GAMMA(t)*(sum((k,j),vawght*(alphakids*tcov(k,j,t)+betawra*tcovwra(k,j,t))*x(k,j,t))));
*benefitvakids ..       BENVAKIDS=e=sum(t,GAMMA(t)*(sum((k,j),vawght*(alphakids*tcov(k,j,t))*x(k,j,t))));
*cost ..                Z=e=sum(t,BETA(t)*(sum((k,j),XCOST(k,j,t))+sum(j,tcostfolate("flour",j,t)))) ;
cost ..                Z=e=sum(t,BETA(t)*(sum((k,j),XCOST(k,j,t)))) ;

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

benefitconst ..         BEN=g=totalbenefits2;
*benefitconst ..        BEN=g=sum(t,BENTIME(t));
*benefitconstva ..      BENVA=g=totalbenefitsbauva;
*benefitconstvakids ..  BENVAKIDS=g=totalbenefitsbauvakids;
*benconstfirst3(t2) ..  BENFIRST3(t2)=g=totalbenefitsbau3(t2);
onesx(j,t)..           sum(k,x(k,j,t))=l=1;
onesy(j,t)..           sum(k,y(k,j,t))=l=1;
*onesw(j,t)..           sum(k,w(k,j,t))=l=1;
*oneswxy(j,t)..         sum(k,x(k,j,t)+y(k,j,t)+w(k,j,t)+v(k,j,t))=l=1;


* equations checking if there is maize, flour, oil and cube anywhere:
yesoileq(j,t)..        yesoil(j,t) =e= sum((oilk),x(oilk,j,t)) ;
yescubeeq(j,t)..       yescube(j,t) =e= sum((cubek),x(cubek,j,t)) ;
yesmaizeeq(j,t)..      yesmaize(j,t) =e= sum((maizek),x(maizek,j,t)) ;
yesdweq(j,t)..         yesdw(j,t) =e= sum((dwk),x(dwk,j,t)) ;
yescapeq(j,t)..        yescap(j,t) =e= sum((capk),x(capk,j,t)) ;
yeszinccubeeq(j,t)..   yeszinccube(j,t) =e= sum((zinccubek),y(zinccubek,j,t)) ;
yesfloureq(j,t)..      yesflour(j,t) =e= sum((flourk),y(flourk,j,t)) ;
yesfolatefloureq(j,t)..yesfolateflour(j,t) =e= sum((folateflourk),y(folateflourk,j,t)) ;
yesfolatecubeeq(j,t).. yesfolatecube(j,t) =e= sum((folatecubek),y(folatecubek,j,t)) ;
yesb12floureq(j,t)..   yesb12flour(j,t) =e= sum((b12flourk),x(b12flourk,j,t)) ;
yesb12cubeeq(j,t)..    yesb12cube(j,t) =e= sum((b12cubek),x(b12cubek,j,t)) ;
yesironfloureq(j,t)..  yesironflour(j,t) =e= sum((ironflourk),x(ironflourk,j,t)) ;
yesironcubeeq(j,t)..   yesironcube(j,t) =e= sum((ironcubek),x(ironcubek,j,t)) ;
yesmnpeq(j,t)..        yesmnpx(j,t) =e= sum((mnpk),x(mnpk,j,t)) ;
yesmnpeq2(j,t)..       yesmnpy(j,t) =e= sum((mnpk),y(mnpk,j,t)) ;

* equations forcing there to be maize, oil, or cube everywhere if it is anywhere:
allnooileq(j,jj,t)..         yesoil(j,t)+yesdw(j,t) =l= 2;
alloileq(j,jj,t)..           yesoil(j,t) =e= yesoil(jj,t) ;
allcubeeq(j,jj,t)..          yescube(j,t) =e= yescube(jj,t) ;
allmaizeeq(j,jj,t)..         yesmaize(j,t) =e= yesmaize(jj,t) ;
alldweq(j,jj,t)..            yesdw(j,t) =e= yesdw(jj,t) ;
allzinccubeeq(j,jj,t)..      yeszinccube(j,t) =e= yeszinccube(jj,t) ;
allb12cubeeq(j,jj,t)..       yesb12cube(j,t) =e= yesb12cube(jj,t) ;
allironcubeeq(j,jj,t)..      yesironcube(j,t) =e= yesironcube(jj,t) ;
allfloureq(j,jj,t)..         yesflour(j,t) =e= yesflour(jj,t) ;
allfolatefloureq(j,jj,t)..   yesfolateflour(j,t) =e= yesfolateflour(jj,t) ;
allfolatecubeeq(j,jj,t)..    yesfolatecube(j,t) =e= yesfolatecube(jj,t) ;
allb12floureq(j,jj,t)..      yesb12flour(j,t) =e= yesb12flour(jj,t) ;
allironfloureq(j,jj,t)..     yesironflour(j,t) =e= yesironflour(jj,t) ;
allmnpeq(j,jj,t)..           yesmnpx(j,t) =e= yesmnpy(j,t) ;
allcubeeq2(j,t2,tt)..        yescube(j,tt) =e= yescube(j,t2) ;
allzinccubeeq2(j,t2,tt)..    yeszinccube(j,tt) =e= yeszinccube(j,t2) ;
allb12cubeeq2(j,t2,tt)..     yesb12cube(j,tt) =e= yesb12cube(j,t2) ;
allironcubeeq2(j,t2,tt)..    yesironcube(j,tt) =e= yesironcube(j,t2) ;
allfolatecubeeq2(j,t2,tt)..  yesfolatecube(j,tt) =e= yesfolatecube(j,t2) ;
*allb12floureq2(j,t2,tt)..    yesb12flour(j,tt) =e= yesb12flour(j,t2) ;
allmaizeeq2(j,t2,tt)..       yesmaize(j,tt) =e= yesmaize(j,t2) ;

yesoileq2(j,t)..        yesoil2(j,t) =e= sum((oilk),w(oilk,j,t)) ;
yescubeeq2(j,t)..       yescube2(j,t) =e= sum((cubek),w(cubek,j,t)) ;
yesmaizeeq2(j,t)..      yesmaize2(j,t) =e= sum((maizek),w(maizek,j,t)) ;

alloileq2(j,jj,t)..     yesoil2(j,t) =e= yesoil2(jj,t) ;
allcubeeq3(j,jj,t)..    yescube2(j,t) =e= yescube2(jj,t) ;
allmaizeeq3(j,jj,t)..   yesmaize2(j,t) =e= yesmaize2(jj,t) ;

yesoileq3(j,t)..        yesoil3(j,t) =e= sum((oilk),w(oilk,j,t)) ;
yescubeeq3(j,t)..       yescube3(j,t) =e= sum((cubek),w(cubek,j,t)) ;
yesmaizeeq3(j,t)..      yesmaize3(j,t) =e= sum((maizek),w(maizek,j,t)) ;

yesoileq4(j,t)..        yesoil4(j,t) =e= sum((oilk),v(oilk,j,t)) ;
yescubeeq4(j,t)..       yescube4(j,t) =e= sum((cubek),v(cubek,j,t)) ;
yesmaizeeq4(j,t)..      yesmaize4(j,t) =e= sum((maizek),v(maizek,j,t)) ;

alloileq3(j,jj,t)..     yesoil3(j,t) =e= yesoil3(jj,t) ;
allcubeeq4(j,jj,t)..    yescube3(j,t) =e= yescube3(jj,t) ;
allmaizeeq4(j,jj,t)..   yesmaize3(j,t) =e= yesmaize3(jj,t) ;

alloileq4(j,jj,t)..     yesoil4(j,t) =e= yesoil4(jj,t) ;
allcubeeq5(j,jj,t)..    yescube4(j,t) =e= yescube4(jj,t) ;
allmaizeeq5(j,jj,t)..   yesmaize4(j,t) =e= yesmaize4(jj,t) ;

allmaizeeq6(j,t2,tt)..       yesmaize2(j,tt) =e= yesmaize2(j,t2) ;
allmaizeeq7(j,t2,tt)..       yesmaize3(j,tt) =e= yesmaize3(j,t2) ;
allcubeeq6(j,t2,tt)..        yescube2(j,tt) =e= yescube2(j,t2) ;
allcubeeq7(j,t2,tt)..        yescube3(j,tt) =e= yescube3(j,t2) ;
allmaizeeq8(j,t2,tt)..       yesmaize4(j,tt) =e= yesmaize4(j,t2) ;
allcubeeq8(j,t2,tt)..        yescube4(j,tt) =e= yescube4(j,t2) ;
* alternative constraint
* fundconst ..         z=l=totalfunds ;

* NOTE: Ideas on how to implement the 3 years of costs without benefits
* Make a parameter or scalar called "sunkcost", to which you give the sunk cost of implementation of cube
* Then add this sunk cost to the cost equation, multiplied by a dummy 1 or 0 depending on whether cube is used
* , call it yescube2 for instance
* Z=e= sum(t,BETA(t)*(sum((k,j),XCOST(k,j,t)))) + sunkcost*yescube2
* Make a variable called "SUNKCOST" which will take the value of 0 if "cube" is never implemented and 1 if it is

* You'll have to define yescube2 in another equation - but I'm not sure how to make it 1 (and not, say, 10)
* yescube2eq..          yescube2 =e= sum((cubek,j,t),x(cubek,j,t)) ;  sums the number of times cube is used.
* one solution would be to define sunkcost over (j,t), then you can just use yescube as already defined in the model
* Z=e= sum(t,BETA(t)*(sum((k,j),XCOST(k,j,t)))) + sum((j,t),sunkcost(j,t)*yescube(j,t) ;
* The bottome line is that it depends what kind of data you have on this sunk cost, and how well you want it disaggregated,
* and whether you want to match it to the year in which it happens.

*Perameters for draws checking on the simulations
Parameter
yesoil_d(draw)           Checks whether a simulation from each draw has oil in it
yescube_d(draw)          Checks whether a simulation from each draw has cube in it
yesfolateflour_d(draw)   Checks whether a simulation from each draw has folate flour in it
yesfolatecube_d(draw)    Checks whether a simulation from each draw has folate cube in it
yesmaize_d(draw)         Checks whether a simulation from each draw has maize in it
yesdw_d(draw)            Checks whether a simulation from each draw has 44% oil in it
yescap_d(j,draw)         Checks whether a simulation from each draw has capsules for each region in it
yescap_d2(j,draw)        Checks the average number of years capsules are used
;


Model nutrition /all/ ;
option minlp=BONMIN ;
Solve nutrition using minlp minimizing z ;
Display  x.l, y.l, z.l, w.l, ben.l, xcov.l, xcost.l, totalfunds;
display  yesoil.l , yescube.l, yesmaize.l, yesdw.l, yesmnpx.l, yesmnpy.l, yesironcube.l, allmaizeeq.l, allcubeeq.l, allironcubeeq.l;
display totalbenefits;



********************START LOOP**************************
s=1;
loop (draw,
execseed=s;
if (s>1,
covnew(k,j,t)= (normal(coveragerobust(k,j,"mean"),coveragerobust(k,j,"sd"))*pop(t,j)) ;
cov(k,j,t)=covnew(k,j,t);
*Max oil simulation 44%-72%-100%
cov("fortoil",j,"1") = (normal(coveragerobust("dwoil",j,"mean"),coveragerobust("dwoil",j,"sd"))*pop("1",j));
cov("capoil",j,"1") = (normal(coveragerobust("capdwoil",j,"mean"),coveragerobust("capdwoil",j,"sd"))*pop("1",j));
cov("oilcube",j,"1") = (normal(coveragerobust("dwoilcube",j,"mean"),coveragerobust("dwoilcube",j,"sd"))*pop("1",j));
cov("capoilcube",j,"1") = (normal(coveragerobust("capdwoilcube",j,"mean"),coveragerobust("capdwoilcube",j,"sd"))*pop("1",j));
cov("capoilmaize",j,"1") = (normal(coveragerobust("capdwoilmaize",j,"mean"),coveragerobust("capdwoilmaize",j,"sd"))*pop("1",j));
cov("oilmaize",j,"1") = (normal(coveragerobust("dwoilmaize",j,"mean"),coveragerobust("dwoilmaize",j,"sd"))*pop("1",j));
cov("oilcubemaize",j,"1") = (normal(coveragerobust("dwoilcubemaize",j,"mean"),coveragerobust("dwoilcubemaize",j,"sd"))*pop("1",j));
cov("capoilcubemaize",j,"1") = (normal(coveragerobust("capdwoilcubemaize",j,"mean"),coveragerobust("capdwoilcubemaize",j,"sd"))*pop("1",j));
cov("fortoil","south","2") = normal(0.188647039,0.056720184)*pop("2","south");
cov("fortoil","north","2") = normal(0.184657986,0.051138841)*pop("2","north");
cov("fortoil","cities","2") = normal(0.361048462,0.052177091)*pop("2","cities");
cov("capoil","south","2") = normal(0.271910918,0.03636394)*pop("2","south");
cov("capoil","north","2") = normal(0.552711992,0.043181427)*pop("2","north");
cov("capoil","cities","2") = normal(0.429750048,0.027707883)*pop("2","cities");
cov("oilcube","south","2") = normal(0.317578384,0.041965529)*pop("2","south");
cov("oilcube","north","2") = normal(0.452445346,0.062957324)*pop("2","north");
cov("oilcube","cities","2") = normal(0.460061855,0.034025083)*pop("2","cities");
cov("capoilcube","south","2") = normal(0.335812702,0.335812702)*pop("2","south");
cov("capoilcube","north","2") = normal(0.66038935,0.66038935)*pop("2","north");
cov("capoilcube","cities","2") = normal(0.481598393,0.481598393)*pop("2","cities");
cov("capoilmaize","south","2") = normal(0.281736205,0.281736205)*pop("2","south");
cov("capoilmaize","north","2") = normal(0.449118915,0.449118915)*pop("2","north");
cov("capoilmaize","cities","2") = normal(0.381499444,0.381499444)*pop("2","cities");
cov("oilmaize","south","2") = normal(0.193206296,0.039506241)*pop("2","south");
cov("oilmaize","north","2") = normal(0.298684737,0.044670404)*pop("2","north");
cov("oilmaize","cities","2") = normal(0.314661303,0.031472923)*pop("2","cities");
cov("oilcubemaize","south","2") = normal(0.281736205,0.038565253)*pop("2","south");
cov("oilcubemaize","north","2") = normal(0.449118915,0.046413903)*pop("2","north");
cov("oilcubemaize","cities","2") = normal(0.381499444,0.033349636)*pop("2","cities");
cov("capoilcubemaize","south","2") = normal(0.331342794,0.032749485)*pop("2","south");
cov("capoilcubemaize","north","2") = normal(0.662643196,0.040875425)*pop("2","north");
cov("capoilcubemaize","cities","2") = normal(0.471177607,0.02437671)*pop("2","cities");

*Costnew is initialized to tcost point estimates before the loop
cstart(k,j,t)    =(costnew(k,j,t)-costnew(k,j,t)*.2)$((costnew(k,j,t))>0);
crobust(k,j,t)   =(costnew(k,j,t)+costnew(k,j,t)*.2)$((costnew(k,j,t))>0);
tcost(k,j,t)     =uniform(cstart(k,j,t),crobust(k,j,t));

else
cov(k,j,t)   = coveragerobust(k,j,"mean")*pop(t,j);
*Max oil simulation 44%-72%-100%
cov("fortoil",j,"1") = coveragerobust("dwoil",j,"mean")*pop("1",j);
cov("capoil",j,"1") = coveragerobust("capdwoil",j,"mean")*pop("1",j);
cov("oilcube",j,"1") = coveragerobust("dwoilcube",j,"mean")*pop("1",j);
cov("capoilcube",j,"1") = coveragerobust("capdwoilcube",j,"mean")*pop("1",j);
cov("capoilmaize",j,"1") = coveragerobust("capdwoilmaize",j,"mean")*pop("1",j);
cov("oilmaize",j,"1") = coveragerobust("dwoilmaize",j,"mean")*pop("1",j);
cov("oilcubemaize",j,"1") = coveragerobust("dwoilcubemaize",j,"mean")*pop("1",j);
cov("capoilcubemaize",j,"1") = coveragerobust("capdwoilcubemaize",j,"mean")*pop("1",j);
cov("fortoil","south","2") = 0.188647039*pop("2","south");
cov("fortoil","north","2") = 0.184657986*pop("2","north");
cov("fortoil","cities","2") = 0.361048462*pop("2","cities");
cov("capoil","south","2") = 0.271910918*pop("2","south");
cov("capoil","north","2") = 0.552711992*pop("2","north");
cov("capoil","cities","2") = 0.429750048*pop("2","cities");
cov("oilcube","south","2") = 0.317578384*pop("2","south");
cov("oilcube","north","2") = 0.452445346*pop("2","north");
cov("oilcube","cities","2") = 0.460061855*pop("2","cities");
cov("capoilcube","south","2") = 0.335812702*pop("2","south");
cov("capoilcube","north","2") = 0.66038935*pop("2","north");
cov("capoilcube","cities","2") = 0.481598393*pop("2","cities");
cov("capoilmaize","south","2") = 0.281736205*pop("2","south");
cov("capoilmaize","north","2") = 0.449118915*pop("2","north");
cov("capoilmaize","cities","2") = 0.381499444*pop("2","cities");
cov("oilmaize","south","2") = 0.193206296*pop("2","south");
cov("oilmaize","north","2") = 0.298684737*pop("2","north");
cov("oilmaize","cities","2") = 0.314661303*pop("2","cities");
cov("oilcubemaize","south","2") = 0.281736205*pop("2","south");
cov("oilcubemaize","north","2") = 0.449118915*pop("2","north");
cov("oilcubemaize","cities","2") = 0.381499444*pop("2","cities");
cov("capoilcubemaize","south","2") = 0.331342794*pop("2","south");
cov("capoilcubemaize","north","2") = 0.662643196*pop("2","north");
cov("capoilcubemaize","cities","2") = 0.471177607*pop("2","cities");
);

display s, tcost, costnew;


display cov, cov2, cov3, covwra, covwra2, covwra3, covzinc, covzinc2, covzinc3, covfolate, covfolate2, covfolate3, covb12wra, covb12wra2,  covb12wra3,
covzincwra, covzincwra2, covzincwra3, coviron, covironwra2, covironwra3, crobust, costnew, tcost ;

display c, c2, c3, czinc, czinc2, czinc3, cmaize, covlist;

*Re-initialize cov2 and cov3
cov2(k,j,t2)      = cov(k,j,t2) ;
cov3(k,j,t3)      = cov(k,j,t3) ;

* cov - subnational - VA
tcov("capsules",j,t)  =cov("capsules",j,t);
tcov("deworming",j,t) =cov("deworming",j,t);
tcov("mnp",j,t)       =cov("mnp",j,t);
tcov("capdw",j,t)     =cov("capdw",j,t);
tcov("capMNP",j,t)    =cov("capmnp",j,t);
tcov("dwmnp",j,t)     =cov("dwmnp",j,t);
tcov("capdwmnp",j,t)  =cov("capdwmnp",j,t);
tcov("cdti",j,t)      =cov("cdti",j,t);
tcov("bcc",j,t)       =cov("bcc",j,t);

* cov - national - VA
tcov("fortoil",j,t)      =cov("fortoil",j,t);
tcov("fortcube",j,t)     =cov3("fortcube",j,t);
tcov("maize",j,t)        =cov3("maize",j,t);
tcov("oilcube",j,t)      =cov2("fortoil",j,t)+cov3("oilcube",j,t);
tcov("oilmaize",j,t)     =cov2("fortoil",j,t)+cov3("oilmaize",j,t);
tcov("cubemaize",j,t)    =cov3("cubemaize",j,t);
tcov("oilcubemaize",j,t) =cov2("fortoil",j,t)+cov3("oilcubemaize",j,t);

* These are all the mixed combinations cov (subnational with national) for VA
tcov("capoil",j,t)               =cov("capoil",j,t);
tcov("capcube",j,t)              =cov2("capsules",j,t)+cov3("capcube",j,t);
tcov("capmaize",j,t)             =cov2("capsules",j,t)+cov3("capmaize",j,t);
tcov("dwoil",j,t)                =cov("dwoil",j,t);
tcov("dwcube",j,t)               =cov2("deworming",j,t)+cov3("dwcube",j,t);
tcov("dwmaize",j,t)              =cov2("deworming",j,t)+cov3("dwmaize",j,t);
tcov("mnpoil",j,t)               =cov("mnpoil",j,t);
tcov("mnpcube",j,t)              =cov2("mnp",j,t)+cov3("mnpcube",j,t);
tcov("mnpmaize",j,t)             =cov2("mnp",j,t)+cov3("mnpmaize",j,t);
tcov("oilcdti",j,t)              =cov("oilcdti",j,t);
tcov("cubecdti",j,t)             =cov2("cdti",j,t)+cov3("cubecdti",j,t);
tcov("maizecdti",j,t)            =cov2("cdti",j,t)+cov3("maizecdti",j,t);
tcov("cubehf",j,t)               =cov2("hf",j,t)+cov3("cubehf",j,t);
tcov("maizehf",j,t)              =cov2("hf",j,t)+cov3("maizehf",j,t);
tcov("oilbcc",j,t)               =cov("oilbcc",j,t);
tcov("cubebcc",j,t)              =cov2("bcc",j,t)+cov3("cubebcc",j,t);
tcov("maizebcc",j,t)             =cov2("bcc",j,t)+cov3("maizebcc",j,t);

tcov("capoilcube",j,t)      =cov2("capoil",j,t)+cov3("capoilcube",j,t);
tcov("dwoilcube",j,t)       =cov2("dwoil",j,t)+cov3("dwoilcube",j,t);
tcov("mnpoilcube",j,t)      =cov2("mnpoil",j,t)+cov3("mnpoilcube",j,t);
tcov("capdwcube",j,t)       =cov2("capdw",j,t)+cov3("capdwcube",j,t);
tcov("capdwoil",j,t)        =cov("capdwoil",j,t);
tcov("capdwmaize",j,t)      =cov2("capdw",j,t)+cov3("capdwmaize",j,t);
tcov("capmnpcube",j,t)      =cov2("capmnp",j,t)+cov3("capmnpcube",j,t);
tcov("capmnpoil",j,t)       =cov("capmnpoil",j,t);
tcov("dwmnpoil",j,t)        =cov("dwmnpoil",j,t);
tcov("capmnpmaize",j,t)     =cov2("capmnp",j,t)+cov3("capmnpmaize",j,t);
tcov("capoilmaize",j,t)     =cov2("capoil",j,t)+cov3("capoilmaize",j,t);
tcov("dwoilmaize",j,t)      =cov2("dwoil",j,t)+cov3("dwoilmaize",j,t);
tcov("oilmnpmaize",j,t)     =cov2("mnpoil",j,t)+cov3("oilmnpmaize",j,t);
tcov("capcubemaize",j,t)    =cov2("capsules",j,t)+cov3("capcubemaize",j,t);
tcov("dwcubemaize",j,t)     =cov2("deworming",j,t)+cov3("dwcubemaize",j,t);
tcov("cubemnpmaize",j,t)    =cov2("mnp",j,t)+cov3("cubemnpmaize",j,t);
tcov("oilcubecdti",j,t)     =cov2("oilcdti",j,t)+cov3("oilcubecdti",j,t);
tcov("oilmaizecdti",j,t)    =cov2("oilcdti",j,t)+cov3("oilmaizecdti",j,t);
tcov("cubemaizecdti",j,t)   =cov2("cdti",j,t)+cov3("cubemaizecdti",j,t);
tcov("oilcubehf",j,t)       =cov2("oilhf",j,t)+cov3("oilcubehf",j,t);
tcov("oilmaizehf",j,t)      =cov2("oilhf",j,t)+cov3("oilmaizehf",j,t);
tcov("cubemaizehf",j,t)     =cov2("hf",j,t)+cov3("cubemaizehf",j,t);
tcov("oilcubebcc",j,t)     =cov2("oilbcc",j,t)+cov3("oilcubebcc",j,t);
tcov("oilmaizebcc",j,t)    =cov2("oilbcc",j,t)+cov3("oilmaizebcc",j,t);
tcov("cubemaizebcc",j,t)   =cov2("bcc",j,t)+cov3("cubemaizebcc",j,t);


tcov("capdwmnpmaize",j,t)        =cov2("capdwmnp",j,t)+cov3("capdwmnpmaize",j,t);
tcov("capdwmnpoil",j,t)          =cov("capdwmnpoil",j,t);
tcov("capdwmnpcube",j,t)         =cov2("capdwmnp",j,t)+cov3("capdwmnpcube",j,t);
tcov("capdwoilcube",j,t)         =cov2("capdwoil",j,t)+cov3("capdwoilcube",j,t);
tcov("capmnpoilcube",j,t)        =cov2("capmnpoil",j,t)+cov3("capmnpoilcube",j,t);
tcov("dwmnpoilcube",j,t)         =cov2("dwmnpoil",j,t)+cov3("dwmnpoilcube",j,t);
tcov("capdwoilmaize",j,t)        =cov2("capdwoil",j,t)+cov3("capdwoilmaize",j,t);
tcov("capoilmnpmaize",j,t)       =cov2("capmnpoil",j,t)+cov3("capoilmnpmaize",j,t);
tcov("dwoilmnpmaize",j,t)        =cov2("dwmnpoil",j,t)+cov3("dwoilmnpmaize",j,t);
tcov("capdwcubemaize",j,t)       =cov2("capdw",j,t)+cov3("capdwcubemaize",j,t);
tcov("capcubemnpmaize",j,t)      =cov2("capmnp",j,t)+cov3("capcubemnpmaize",j,t);
tcov("dwcubemnpmaize",j,t)       =cov2("dwmnp",j,t)+cov3("dwcubemnpmaize",j,t);
tcov("capoilcubemaize",j,t)      =cov2("capoil",j,t)+cov3("capoilcubemaize",j,t);
tcov("dwoilcubemaize",j,t)       =cov2("dwoil",j,t)+cov3("dwoilcubemaize",j,t);
tcov("oilcubemnpmaize",j,t)      =cov2("mnpoil",j,t)+cov3("oilcubemnpmaize",j,t);
tcov("oilcubemaizecdti",j,t)     =cov2("oilcdti",j,t)+cov3("oilcubemaizecdti",j,t);
tcov("oilcubemaizehf",j,t)       =cov2("oilhf",j,t)+cov3("oilcubemaizehf",j,t);
tcov("oilcubemaizebcc",j,t)      =cov2("oilbcc",j,t)+cov3("oilcubemaizebcc",j,t);

tcov("capdwmnpoilcube",j,t)=cov2("capdwmnpoil",j,t)+cov3("capdwmnpoilcube",j,t);
tcov("capdwcubemnpmaize",j,t)=cov2("capdwmnp",j,t)+cov3("capdwcubemnpmaize",j,t);
tcov("capdwoilmnpmaize",j,t)=cov2("capdwmnpoil",j,t)+cov3("capdwoilmnpmaize",j,t);
tcov("capdwoilcubemaize",j,t)=cov2("capdwoil",j,t)+cov3("capdwoilcubemaize",j,t);
tcov("capoilcubemnpmaize",j,t)=cov2("capmnpoil",j,t)+cov3("capoilcubemnpmaize",j,t);
tcov("dwoilcubemnpmaize",j,t)=cov2("dwmnpoil",j,t)+cov3("dwoilcubemnpmaize",j,t);

tcov("capdwoilcubemnpmaize",j,t)=cov2("capdwmnpoil",j,t)+cov3("capdwoilcubemnpmaize",j,t);

*List Results when we have flour, cube and flourcube
*tcovflourcube(k,j,t)=tcov(k,j,t) ;

*Reset cov to no folate combinations instead of flourcube
*cov(k,j,t)=deathsaverted4(j,t,k) ;
*cov2(k,j,t2)=deathsaverted4(j,t2,k) ;
*cov3(k,j,t3)=deathsaverted4(j,t3,k) ;

* cov - subnational - VA
tcov("capsules",j,t)  =cov("capsules",j,t);
tcov("deworming",j,t) =cov("deworming",j,t);
tcov("mnp",j,t)       =cov("mnp",j,t);
tcov("capdw",j,t)     =cov("capdw",j,t);
tcov("capMNP",j,t)    =cov("capmnp",j,t);
tcov("dwmnp",j,t)     =cov("dwmnp",j,t);
tcov("capdwmnp",j,t)  =cov("capdwmnp",j,t);
tcov("cdti",j,t)      =cov("cdti",j,t);
tcov("bcc",j,t)       =cov("bcc",j,t);

* cov - national - VA
tcov("fortoil",j,t)      =cov("fortoil",j,t);
tcov("fortcube",j,t)     =cov3("fortcube",j,t);
tcov("maize",j,t)        =cov3("maize",j,t);
tcov("oilcube",j,t)      =cov2("fortoil",j,t)+cov3("oilcube",j,t);
tcov("oilmaize",j,t)     =cov2("fortoil",j,t)+cov3("oilmaize",j,t);
tcov("cubemaize",j,t)    =cov3("cubemaize",j,t);
tcov("oilcubemaize",j,t) =cov2("fortoil",j,t)+cov3("oilcubemaize",j,t);

* These are all the mixed combinations cov (subnational with national) for VA
tcov("capoil",j,t)               =cov("capoil",j,t);
tcov("capcube",j,t)              =cov2("capsules",j,t)+cov3("capcube",j,t);
tcov("capmaize",j,t)             =cov2("capsules",j,t)+cov3("capmaize",j,t);
tcov("dwoil",j,t)                =cov("dwoil",j,t);
tcov("dwcube",j,t)               =cov2("deworming",j,t)+cov3("dwcube",j,t);
tcov("dwmaize",j,t)              =cov2("deworming",j,t)+cov3("dwmaize",j,t);
tcov("mnpoil",j,t)               =cov("mnpoil",j,t);
tcov("mnpcube",j,t)              =cov2("mnp",j,t)+cov3("mnpcube",j,t);
tcov("mnpmaize",j,t)             =cov2("mnp",j,t)+cov3("mnpmaize",j,t);
tcov("oilcdti",j,t)              =cov("oilcdti",j,t);
tcov("cubecdti",j,t)             =cov2("cdti",j,t)+cov3("cubecdti",j,t);
tcov("maizecdti",j,t)            =cov2("cdti",j,t)+cov3("maizecdti",j,t);
tcov("cubehf",j,t)               =cov2("hf",j,t)+cov3("cubehf",j,t);
tcov("maizehf",j,t)              =cov2("hf",j,t)+cov3("maizehf",j,t);
tcov("oilbcc",j,t)               =cov("oilbcc",j,t);
tcov("cubebcc",j,t)              =cov2("bcc",j,t)+cov3("cubebcc",j,t);
tcov("maizebcc",j,t)             =cov2("bcc",j,t)+cov3("maizebcc",j,t);

tcov("capoilcube",j,t)      =cov2("capoil",j,t)+cov3("capoilcube",j,t);
tcov("dwoilcube",j,t)       =cov2("dwoil",j,t)+cov3("dwoilcube",j,t);
tcov("mnpoilcube",j,t)      =cov2("mnpoil",j,t)+cov3("mnpoilcube",j,t);
tcov("capdwcube",j,t)       =cov2("capdw",j,t)+cov3("capdwcube",j,t);
tcov("capdwoil",j,t)        =cov("capdwoil",j,t);
tcov("capdwmaize",j,t)      =cov2("capdw",j,t)+cov3("capdwmaize",j,t);
tcov("capmnpcube",j,t)      =cov2("capmnp",j,t)+cov3("capmnpcube",j,t);
tcov("capmnpoil",j,t)       =cov("capmnpoil",j,t);
tcov("dwmnpoil",j,t)        =cov("dwmnpoil",j,t);
tcov("capmnpmaize",j,t)     =cov2("capmnp",j,t)+cov3("capmnpmaize",j,t);
tcov("capoilmaize",j,t)     =cov2("capoil",j,t)+cov3("capoilmaize",j,t);
tcov("dwoilmaize",j,t)      =cov2("dwoil",j,t)+cov3("dwoilmaize",j,t);
tcov("oilmnpmaize",j,t)     =cov2("mnpoil",j,t)+cov3("oilmnpmaize",j,t);
tcov("capcubemaize",j,t)    =cov2("capsules",j,t)+cov3("capcubemaize",j,t);
tcov("dwcubemaize",j,t)     =cov2("deworming",j,t)+cov3("dwcubemaize",j,t);
tcov("cubemnpmaize",j,t)    =cov2("mnp",j,t)+cov3("cubemnpmaize",j,t);
tcov("oilcubecdti",j,t)     =cov2("oilcdti",j,t)+cov3("oilcubecdti",j,t);
tcov("oilmaizecdti",j,t)    =cov2("oilcdti",j,t)+cov3("oilmaizecdti",j,t);
tcov("cubemaizecdti",j,t)   =cov2("cdti",j,t)+cov3("cubemaizecdti",j,t);
tcov("oilcubehf",j,t)       =cov2("oilhf",j,t)+cov3("oilcubehf",j,t);
tcov("oilmaizehf",j,t)      =cov2("oilhf",j,t)+cov3("oilmaizehf",j,t);
tcov("cubemaizehf",j,t)     =cov2("hf",j,t)+cov3("cubemaizehf",j,t);
tcov("oilcubebcc",j,t)     =cov2("oilbcc",j,t)+cov3("oilcubebcc",j,t);
tcov("oilmaizebcc",j,t)    =cov2("oilbcc",j,t)+cov3("oilmaizebcc",j,t);
tcov("cubemaizebcc",j,t)   =cov2("bcc",j,t)+cov3("cubemaizebcc",j,t);


tcov("capdwmnpmaize",j,t)        =cov2("capdwmnp",j,t)+cov3("capdwmnpmaize",j,t);
tcov("capdwmnpoil",j,t)          =cov("capdwmnpoil",j,t);
tcov("capdwmnpcube",j,t)         =cov2("capdwmnp",j,t)+cov3("capdwmnpcube",j,t);
tcov("capdwoilcube",j,t)         =cov2("capdwoil",j,t)+cov3("capdwoilcube",j,t);
tcov("capmnpoilcube",j,t)        =cov2("capmnpoil",j,t)+cov3("capmnpoilcube",j,t);
tcov("dwmnpoilcube",j,t)         =cov2("dwmnpoil",j,t)+cov3("dwmnpoilcube",j,t);
tcov("capdwoilmaize",j,t)        =cov2("capdwoil",j,t)+cov3("capdwoilmaize",j,t);
tcov("capoilmnpmaize",j,t)       =cov2("capmnpoil",j,t)+cov3("capoilmnpmaize",j,t);
tcov("dwoilmnpmaize",j,t)        =cov2("dwmnpoil",j,t)+cov3("dwoilmnpmaize",j,t);
tcov("capdwcubemaize",j,t)       =cov2("capdw",j,t)+cov3("capdwcubemaize",j,t);
tcov("capcubemnpmaize",j,t)      =cov2("capmnp",j,t)+cov3("capcubemnpmaize",j,t);
tcov("dwcubemnpmaize",j,t)       =cov2("dwmnp",j,t)+cov3("dwcubemnpmaize",j,t);
tcov("capoilcubemaize",j,t)      =cov2("capoil",j,t)+cov3("capoilcubemaize",j,t);
tcov("dwoilcubemaize",j,t)       =cov2("dwoil",j,t)+cov3("dwoilcubemaize",j,t);
tcov("oilcubemnpmaize",j,t)      =cov2("mnpoil",j,t)+cov3("oilcubemnpmaize",j,t);
tcov("oilcubemaizecdti",j,t)     =cov2("oilcdti",j,t)+cov3("oilcubemaizecdti",j,t);
tcov("oilcubemaizehf",j,t)       =cov2("oilhf",j,t)+cov3("oilcubemaizehf",j,t);
tcov("oilcubemaizebcc",j,t)      =cov2("oilbcc",j,t)+cov3("oilcubemaizebcc",j,t);

tcov("capdwmnpoilcube",j,t)=cov2("capdwmnpoil",j,t)+cov3("capdwmnpoilcube",j,t);
tcov("capdwcubemnpmaize",j,t)=cov2("capdwmnp",j,t)+cov3("capdwcubemnpmaize",j,t);
tcov("capdwoilmnpmaize",j,t)=cov2("capdwmnpoil",j,t)+cov3("capdwoilmnpmaize",j,t);
tcov("capdwoilcubemaize",j,t)=cov2("capdwoil",j,t)+cov3("capdwoilcubemaize",j,t);
tcov("capoilcubemnpmaize",j,t)=cov2("capmnpoil",j,t)+cov3("capoilcubemnpmaize",j,t);
tcov("dwoilcubemnpmaize",j,t)=cov2("dwmnpoil",j,t)+cov3("dwoilcubemnpmaize",j,t);

tcov("capdwoilcubemnpmaize",j,t)=cov2("capdwmnpoil",j,t)+cov3("capdwoilcubemnpmaize",j,t);
display tcov ;

* Equation for BAU* total benefits, using weights and discount factor
totalbenefitsbau=sum(t,GAMMA(t)*(sum((j),vawght*(alphakids*tcov("capdwoil",j,t)+betawra*tcovwra("fortoil",j,t))
                        +zincwght*(zinckidwght*tcovzinc("flour",j,t)+zincwrawght*tcovzincwra("flour",j,t))+ironwght*(ironkidwght*tcoviron("flour",j,t)+ironwrawght*tcovironwra("flour",j,t))+
                        folatewght*(folatekidwght*tcovfolate("flour",j,t))+b12wght*(b12kidwght*tcovb12("flour",j,t))+b12wght*(b12wrawght*tcovb12wra("flour",j,t)))));

totalbenefitsbau2(j)=sum(t,GAMMA(t)*(vawght*(alphakids*tcov("capdwoil",j,t)+betawra*tcovwra("fortoil",j,t))
                        +zincwght*(zinckidwght*tcovzinc("flour",j,t)+zincwrawght*tcovzincwra("flour",j,t)+b12wght*(b12wrawght*tcovb12wra("flour",j,t)))));

totalbenefitsbau3(t)=sum(j,GAMMA(t)*(vawght*(alphakids*tcov("capdwoil",j,t)+betawra*tcovwra("fortoil",j,t))
                        +zincwght*(zinckidwght*tcovzinc("flour",j,t)+zincwrawght*tcovzincwra("flour",j,t))+b12wght*(b12wrawght*tcovb12wra("flour",j,t))));

totalbenefitsbau4(j,t)=GAMMA(t)*(vawght*(alphakids*tcov("capdwoil",j,t)+betawra*tcovwra("fortoil",j,t))
                        +zincwght*(zinckidwght*tcovzinc("flour",j,t)+zincwrawght*tcovzincwra("flour",j,t)));

totalbenefitsbauva=sum(t,GAMMA(t)*(sum((j),vawght*(alphakids*tcov("capdwoil",j,t)+betawra*tcovwra("fortoil",j,t)))));

totalbenefitsbauvakids=sum(t,GAMMA(t)*(sum((j),vawght*(alphakids*tcov("capdwoil",j,t)))));

totalbenefits2=percben*totalbenefitsbau ;

*Include or not include alternative platforms
tcov(cdtik,j,t) = includecdti*tcov(cdtik,j,t) ;
tcov(hfk,j,t) = includehf*tcov(hfk,j,t) ;
*tcov(dwk,j,t) = includedw*tcov(dwk,j,t) ;

option minlp=BONMIN ;
Solve nutrition using minlp minimizing z ;
Display  tcost, covnew, x.l, y.l, z.l, ben.l, xcov.l, xcost.l, onesx.l, totalfunds;
display  yesoil.l , yescube.l, yesmaize.l, yesdw.l, yesmnpx.l, yesmnpy.l, yesironcube.l, allmaizeeq.l, allcubeeq.l, allironcubeeq.l;
display totalbenefits;

totalcost_d(draw)=sum((k,j,t), xcost.l(k,j,t));
totalben_d(draw) =sum((k,j,t), xcov.l(k,j,t));
totalcb_d(draw)  =sum((k,j,t), xcost.l(k,j,t))/sum((k,j,t), xcov.l(k,j,t));
yesoil_d(draw)   =sum((j,t),yesoil.l(j,t))>3 ;
yescube_d(draw)  =sum((j,t),yescube.l(j,t))>3 ;
yesmaize_d(draw) =sum((j,t),yesmaize.l(j,t))>3 ;
yesdw_d(draw)    =sum((j,t),yesdw.l(j,t))>0.1 ;
*Not sure why but it has to be greater than 1.1 instead of 1 to be in more than one area.
yescap_d(j,draw)=sum(t,yescap.l(j,t))>0.1 ;
yescap_d2(j,draw)=sum(t,yescap.l(j,t))   ;
s=s+1;
);

Parameters
finalcov         Coverage per time period all
finalcovvakids   Coverage per time period VA kids
finalcovvawra    Coverage per time period VA WRA
finalcovzinckids Coverage per time period Zinc kids
finalcovzincwra  Coverage per time period Zinc WRA
finalcovfolatekids Coverage per time period Folate kids
finalcovfolatewra  Coverage per time period Folate WRA
finalcovb12wra   Coverage per time period B12 WRA
finalcovironkids Coverage per time period Iron kids
finalcost        Cost per time period
finalcovspace    Coverage per space for variables by space
finalcostspace   Cost per space for variables by space
covbau           Coverage per time for BAU scenario
costbau          Cost per time for BAU scenario
covbauvakids     Coverage per time for BAU scenario
covbauvawra      Coverage per time for BAU scenario
covbauzinckids   Coverage per time for BAU scenario
covbauzincwra    Coverage per time for BAU scenario
covbauironkids   Coverage per time for BAU scenario
covbauironwra    Coverage per time for BAU scenario WRA Iron
covbaub12wra     Coverage per time for BAU scenario
covbauspace      Coverage per space for BAU scenario
costbau          Cost per time for BAU scenario
costbauspace     Cost per space for BAU scenario
test1           Testing
test2           Testing
test3           Testing
test4           Testing
test5           Testing
test6           Testing
test7           Testing
test8           Testing
test9           Testing
yesoil_pct      Percentage of times that oil appears in the optimal solution
yescube_pct     Percentage of times that cube appears in the optimal solution
yesdw_pct       Percentage of times that 44% oil appears in the optimal solution
yesfolateflour_pct    Percentage of times that folate flour appears in the optimal solution
yesfolatecube_pct     Percentage of times that folate cube appears in the optimal solution
yesmaize_pct    Percentage of times that maize appears in the optimal solution
yescap_pct(j)   Percentage of times that capsules appears in the optimal solution
yescap_avg(j)   average number of years (by region) of times that capsules appears in the optimal solution
;

finalcov(t)              =sum(k,sum(j,xcov.l(k,j,t)))  ;
finalcovvawra(t)         =vawght*1*sum(k,sum(j,tcovwra(k,j,t)*x.l(k,j,t)));
finalcovvakids(t)        =vawght*alphakids*sum(k,sum(j,tcov(k,j,t)*x.l(k,j,t)));
finalcovzincwra(t)       =sum(k,sum(j,tcovzincwra(k,j,t)*y.l(k,j,t)));
finalcovzinckids(t)      =sum(k,sum(j,tcovzinc(k,j,t)*y.l(k,j,t)));
*finalcovfolatewra(t)     =sum(k,sum(j,tcovfolatewra(k,j,t)*x.l(k,j,t)));
finalcovfolatekids(t)    =sum(k,sum(j,tcovfolate(k,j,t)*x.l(k,j,t)));
finalcovb12wra(t)        =sum(k,sum(j,tcovb12wra(k,j,t)*x.l(k,j,t)));
finalcost(t)             =sum(k,sum(j,xcost.l(k,j,t))) ;
finalcostspace(j)        =sum(k,sum(t,xcost.l(k,j,t))) ;
finalcovspace(j)         =sum(k,sum(t,xcov.l(k,j,t)))  ;
covbauvakids(t)          =sum(j,tcov("capoil",j,t))  ;
covbauvawra(t)           =sum(j,tcovwra("fortoil",j,t))  ;
covbauzinckids(t)        =sum(j,tcovzinc("flour",j,t))  ;
covbauzincwra(t)         =sum(j,tcovzincwra("flour",j,t))  ;
covbauironkids(t)        =sum(j,tcoviron("flour",j,t))  ;
covbaub12wra(t)          =sum(j,tcovfolatewra("flour",j,t))  ;
covbauironwra(t)         =sum(j,tcovfolate("flour",j,t))  ;
covbau(t)                =sum(j,tcov("capdwoil",j,t))  ;
costbau(t)               =sum(j,tcost("capdwoil",j,t))  ;
covbauspace(j)           =sum(t,tcov("capdwoil",j,t))  ;
costbauspace(j)          =sum(t,tcost("capdwoil",j,t))  ;
test1                    =sum((j,t),tcov("capdwoil",j,t))  ;
test2                    =sum((j,t),tcost("capdwoil",j,t))  ;
test3(j)                 =sum(t,tcov("capdwoilcube",j,t));
test4(j,t)          =tcost("capsules",j,t);
test5(j,t)          =tcov("capoilcube",j,t)-tcov("capcube",j,t);
test6(j,t)          =tcov("capoilcube",j,t)-tcov("capoil",j,t);
test7(j,t)          =tcov("oilcube",j,t)-tcov("fortcube",j,t);
test8(j,t)          =tcov("oilcube",j,t)-tcov("fortoil",j,t);
test9(t)            =finalcov(t) ;
yesoil_pct          =(sum(draw, yesoil_d(draw))/card(draw))*100;
yescube_pct         =(sum(draw, yescube_d(draw))/card(draw))*100;
yesmaize_pct        =(sum(draw, yesmaize_d(draw))/card(draw))*100;
yesdw_pct           =(sum(draw, yesdw_d(draw))/card(draw))*100;
yescap_pct(j)       =(sum(draw, yescap_d(j,draw))/card(draw))*100;
yescap_avg(j)       =(sum(draw, yescap_d2(j,draw))/card(draw));


* Try to separate parameters and variables:
Display c,  totalfunds,   finalcost, finalcov, finalcostspace, finalcovspace, finalcovvawra, finalcovvakids,
       finalcovzincwra, finalcovzinckids,  finalcovfolatekids, finalcovb12wra,
        covbauvakids, covbauvawra, covbauzinckids, covbauzincwra, covbauironkids, covbauironwra, covbaub12wra, costbau, covbau, covbauspace, costbauspace,
       c2, BETA, test1, test2, test3, test4, test5, test6, test7, test8, test9, yescap_d, yescap_avg;
*-----------------------------------------------------------------------
* Now output parameters with mean and variance
*-----------------------------------------------------------------------
set mv /mean, stdev, pct5, pct95/ ;

*abort$(card(draw) le 1) "ONE REPETITION ONLY - NO MEANS OR STDEVS TO COMPUTE";
* Welfare and efficiency
parameter
         totalcost_mv(mv)         total cost
         totalben_mv(mv)          total ben
         totalcb_mv(mv)           total cost per ben
         totalcost_mv2(mv)         total cost
         totalben_mv2(mv)          total ben
         totalcb_mv2(mv)           total cost per ben
         totalcost_dmean(draw)     deviation from the mean for total cost
         totalben_dmean(draw)      deviation from the mean for total benefits
         totalcb_dmean(draw)       deviation from the mean for total cost per benefit
;




totalcost_mv("mean") = sum(draw, totalcost_d(draw)) / card(draw) ;
totalcost_mv("stdev") = sqrt(sum(draw, sqr(totalcost_d(draw) - totalcost_mv("mean")))/(card(draw)-1)) ;
totalben_mv("mean") = sum(draw, totalben_d(draw)) / card(draw) ;
totalben_mv("stdev") = sqrt(sum(draw, sqr(totalben_d(draw) - totalben_mv("mean")))/(card(draw)-1)) ;
totalcb_mv("mean") = sum(draw, totalcb_d(draw)) / card(draw) ;
totalcb_mv("stdev") = sqrt(sum(draw, sqr(totalcb_d(draw) - totalcb_mv("mean")))/(card(draw)-1)) ;

totalcost_mv2("mean") = totalcost_d("dr0") ;
totalcost_dmean(draw) = totalcost_d(draw) - totalcost_d("dr0") ;
totalcost_mv2("stdev") = sqrt(sum(draw, sqr(totalcost_d(draw) - totalcost_mv2("mean")))/(card(draw)-1)) ;
totalben_mv2("mean") = totalben_d("dr0") ;
totalben_dmean(draw) = totalben_d(draw) - totalben_d("dr0") ;
totalben_mv2("stdev") = sqrt(sum(draw, sqr(totalben_d(draw) - totalben_mv2("mean")))/(card(draw)-1)) ;
totalcb_mv2("mean") = totalcb_d("dr0") ;
totalcb_dmean(draw) = totalcb_d(draw) - totalcb_d("dr0") ;
totalcb_mv2("stdev") = sqrt(sum(draw, sqr(totalcb_d(draw) - totalcb_mv2("mean")))/(card(draw)-1)) ;

display finalcost, totalcost_mv, totalcost_mv2, totalben_mv, totalben_mv2, totalcb_mv, totalcb_mv2, totalcost_dmean, totalben_dmean, totalcb_dmean;
* Computing the lower and higher confidence bounds:
*---------------------------------------------------------------------
set lh(mv) /pct5, pct95 /
parameter Torank(draw)
         Ranks(draw)
* add percentiles to "ci" if you want to know more percentile values,
* for instance adding ", med 50" will compute 50th percentile and call it "med"
* (note: in that example you must also add "med" to the mv and lh sets)
* Note: this is a 95% CI, even though it is named as a 90% one
         ci(lh) confidence interval definition /pct5 2.5, pct95 97.5/
         ci2(lh) confidence intervals (values) ;

* this initialises the use of the "rank" procedure (native to GAMS)
$libinclude rank

* yD(h)
* This loops over all the household and, for each one, ranks the values of incomes
* and computes the percentiles we chose to compute in the "ci" parameter.
* This is looped because the "rank" procedure only works for one-dimentional parameters,
* so we make a one-dimentional parameter and overwrite it for each household in turn.

* Use this operation for all the parameters we want confidence bounds for:
*--------------------------------------------------------------------------------

* Total costs overall
ci2(lh) = ci(lh);
$libinclude rank totalcost_d draw Ranks ci2
totalcost_mv(lh) = ci2(lh) ;
display ci, ci2, totalcost_d, totalcost_mv ;

* Total benefits overall
ci2(lh) = ci(lh);
$libinclude rank totalben_d draw Ranks ci2
totalben_mv(lh) = ci2(lh) ;
display  Ranks, totalben_d, totalben_mv ;

* Total costs per benefit overall
ci2(lh) = ci(lh);
$libinclude rank totalcb_d draw Ranks ci2
totalcb_mv(lh) = ci2(lh) ;
display totalcb_mv ;

*Hanqi estimates using point estimates rather than means of monte carlo
* Total costs overall
ci2(lh) = ci(lh);
$libinclude rank totalcost_dmean draw Ranks ci2
totalcost_mv2("pct95") = totalcost_mv2("mean")-ci2("pct95") ;
totalcost_mv2("pct5") = totalcost_mv2("mean")-ci2("pct5") ;
display ci, ci2, totalcost_dmean, totalcost_mv2 ;

* Total benefits overall
ci2(lh) = ci(lh);
$libinclude rank totalben_dmean draw Ranks ci2
totalben_mv2("pct95") = totalben_mv2("mean")-ci2("pct95") ;
totalben_mv2("pct5") = totalben_mv2("mean")-ci2("pct5") ;
display  Ranks, totalben_dmean, totalben_mv2 ;

* Total costs per benefit overall
ci2(lh) = ci(lh);
$libinclude rank totalcb_dmean draw Ranks ci2
totalcb_mv2("pct95") = totalcb_mv2("mean")-ci2("pct95") ;
totalcb_mv2("pct5") = totalcb_mv2("mean")-ci2("pct5") ;
display Ranks, totalcb_dmean, totalcb_mv2 ;
* #################################################################################################
* ################################# OUTPUT THE TABLE WITH A PUT STATEMENT #########################
* #################################################################################################
* (This is useful to automate certain kinds of output and avoid repetitive excel manipulations
* It makes a text file (table1.txt) which can be easily cut and pasted into excel.

* OUTPUT: after the run, open the following .txt file.
* It can be cut+pasted to excel for easy comparison between runs
* (do a text-to-columns with semicolon as the separator)
file tablput20_4bk /table3.txt/;
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

put 'Total coverage by space for bau* and optimal model' /;
loop(j,
    put j.tl 'bau*';
    put  @45';' covbauspace(j):12:0 /;
);
loop(j,
    put j.tl 'optimal model';
    put  @45';' finalcovspace(j):12:0 /;
);
put //;


put 'Coverage VA Kids 6-59months' /;
loop(t,
    put t.tl;
    put  @45';' finalcovvakids(t):12:2 /;
);
put //;

put 'Coverage VA WRA' /;
loop(t,
    put t.tl;
    put  @45';' finalcovvawra(t):12:2 /;
);
put //;

put 'Coverage Zinc Kids 6-59months' /;
loop(t,
    put t.tl;
    put  @45';' finalcovzinckids(t):12:2 /;
);
put //;

put 'Coverage Zinc WRA' /;
loop(t,
    put t.tl;
    put  @45';' finalcovzincwra(t):12:2 /;
);
put //;

put 'Coverage Folate Kids 6-59months' /;
loop(t,
    put t.tl;
    put  @45';' finalcovfolatekids(t):12:2 /;
);
put //;

put 'Coverage B12 WRA BAU' /;
loop(t,
    put t.tl;
    put  @45';' covbaub12wra(t):12:2 /;
);
put //;

put 'Coverage IRON BAU' /;
loop(t,
    put t.tl;
    put  @45';' covbauironkids(t):12:2 /;
);
put //;

put 'Marginal coverages by year: test 1' /;
loop(t,
    put t.tl;
loop(j,
    put j.tl;
*     put  @45';' test1(j,t):12:2 /;
);
);


put //;
put / ;
put 'iterations'  @40'; ' card(draw
) /;
put / ;

put / ;
put 'percent oil'  @40'; ' yesoil_pct '%' /;
put / ;

put / ;
put 'percent cube'  @40'; ' yescube_pct '%' /;
put / ;

put / ;
put 'percent maize'  @40'; ' yesmaize_pct '%' /;
put / ;


put / ;
put 'percent unenhanced oil'  @40'; ' yesdw_pct '%' /;
put / ;


put 'Total Costs' /;
put  @45';' totalcost_mv("mean"):<12:0 /;
put @14 '(CI)' @40 ';' '(' totalcost_mv("pct5"):12:0 '-' totalcost_mv("pct95"):12:0  ')'/ ;

put /;

put 'Total Benefits' /;
put  @45';' totalben_mv("mean"):<12:0 /;
put @14 '(CI)' @40 ';' '(' totalben_mv("pct5"):12:0 '-' totalben_mv("pct95"):12:0  ')'/ ;

put /;

put 'Total Cost per Benefit' /;
put  @45';' totalcb_mv("mean"):<6.2 /;
put @14 '(CI)' @40 ';' '(' totalcb_mv("pct5"):6:2 '-' totalcb_mv("pct95"):6.2  ')'/ ;

put /;

put 'Hanqi Estimates' /;

put 'Total Costs' /;
put  @45';' totalcost_mv2("mean"):<12:0 /;
put @14 '(CI)' @40 ';' '(' totalcost_mv2("pct95"):12:0 '-' totalcost_mv2("pct5"):12:0  ')'/ ;

put /;

put 'Total Benefits' /;
put  @45';' totalben_mv2("mean"):<12:0 /;
put @14 '(CI)' @40 ';' '(' totalben_mv2("pct95"):12:0 '-' totalben_mv2("pct5"):12:0  ')'/ ;

put /;

put 'Total Cost per Benefit' /;
put  @45';' totalcb_mv2("mean"):<6.2 /;
put @14 '(CI)' @40 ';' '(' totalcb_mv2("pct95"):6:2 '-' totalcb_mv2("pct5"):6.2  ')'/ ;

put /;


put 'Percent CHD-VAS by Macro-Region' /;
loop(j,
    put j.tl;
    put  @45';' yescap_pct(j):12:2 '%' /;
);

put 'Average years CHD-VAS by Macro-Region' /;
loop(j,
    put j.tl;
    put  @45';' yescap_avg(j):12:2 ' years' /;
);

