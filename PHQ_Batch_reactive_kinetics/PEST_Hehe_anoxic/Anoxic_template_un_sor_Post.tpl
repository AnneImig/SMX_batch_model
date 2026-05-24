ptf $
Title Anoxic Template sorption and undetected

SOLUTION_MASTER_SPECIES
Som           Som              0       32              32  
Doc           Doc              0       32              32
Undet         Undet            0       250             250
Docr          Docr             0       32              32
Amonia        Amonia           0       18              18
Nit           Nit-             0       47              47
Ammet         Ammet            0       Ammet           98.1
Smz           Smz              0       Smz             278.33
Smx           Smx              0       Smx             253.28
Sdz           Sdz              0       Sdz             250.278
Des           Des              0       Des             238.26
Nitro	      Nitro            0       Nitro           283.26


SURFACE_MASTER_SPECIES
Sediment Sediment     

SOLUTION_SPECIES
Som = Som
    log_k     0
Undet =Undet
    log_k     0
Doc = Doc
    log_k     0
Docr = Docr
    log_k     0
Amonia = Amonia
    log_k     0
Nit- = Nit-
    log_k     0
Nit- + H+ = H(Nit)
	log_k -3.4
Smz= Smz
    log_k 0
Sdz= Sdz
    log_k 0
Smx = Smx
    log_k 0
Ammet= Ammet
    log_k 0
Des= Des
    log_k 0
Nitro =Nitro
    log_k 0

SURFACE_SPECIES
Sediment =Sediment 
    log_k   0
Nitro + Sediment= NitroSediment
    log_k -100.2
    mole_balance NitroSediment
Des + Sediment= DesSediment
    log_k -101.2
    mole_balance DesSediment
Ammet + Sediment= AmmetSediment
    log_k -101.2
    mole_balance AmmetSediment
Smx + Sediment= SmxSediment
    log_k -101.45
    mole_balance SmxSediment

SURFACE 
    Sediment 1e100 1 1
    equil 1
    no_edl true


SOLUTION 1 Infiltration water
    pH    		7.13 # pH 7.13 of the soil Ma et al. 2023
    temp    	20 #Ma et al. 2023
    units     mol/kgw
    density   1
#Drikke vand 16 Juni 2023 GEUS very similar to 20 Februar 2020
    N(+5)     2.19E-04 #NO3-
    Amonia    2.18404E-05
    C(4)      0.003 #HCO3
    Ca 		  3e-03   #120 mg/L
    Cl		  88 mg/kgw charge #Cl 0.013  charge
    K 		  5 mg/kgw
    Mg 		  23 mg/kgw
    Mn 		  0.001	mg/kgw
    Na  	  66 mg/kgw 	
    O(0)	  8.2 mg/kgw
    Doc       3.28 mg/kgw   
    Smz       0.01 mg/kgw
    Smx       0.01 mg/kgw
    Sdz       0.01 mg/kgw
    -water    1 # kg



Equilibrium_phases  1
Calcite 0 0
Goethite 0 0.1
Incremental_Reactions True    #less CPU intensive, other way of integrating time steps

##################   KINETICS   #####################
KINETICS 


Som
    -formula  Docr 1 Amonia 0.02
       -m0    0.015        
       -parms    $K1               $
    -steps  0 300*0.1          #30 days in 300 time steps?

Doc_r
    -formula Docr  -1 Doc  1 
    # Kmax = mol Docr / day 
       -parms    $K2            $   

Doc_Degradation_NITu
    -formula  Doc  -1 Nit- +2.2 NO3- -2.2 C+4 1
    #(1) K6 
       -parms    $K6              $  

Doc_Degradation_NITdos
    -formula  Doc  -6 Nit- -8 N2 +4 C+4 6 
    # (1) K7 (2)  inhib_NO3 
       -parms    $K7     $  $K_NO3    $ 

######### Antibiotics forward ########################
#sulfonamide transforamtion#

Smx_Ammet
    -formula Smx -1    Ammet 1
    #	 k8 ( mol SMX/mol time)   	(2) inhib DOC 
       -parms     $K8       $  $K_DOC            $
     #super sensitive only starting with numbers higher than 6e80

Smx_NIT
    -formula Smx -1 Nitro 1
       -parms    $K9           $


Smx_DES_N
    -formula     Des 1 Smx -1  H(Nit) -1 Doc -1 C+4 +1 
    #  	 k10 ( mol SMX/mol time)  	 
       -parms    $K10       $

Smx_DES_O
    -formula      Smx -1 Des +1 
    #  	 k11 ( mol SMX/mol time)  
       -parms    $K11        $

Des_NIT_N
     -formula    Des -1    Nitro +1  H+1 -1
#      	  	k12  (anoxic mol SMX/mol time )
       -parms    $K12           $

NIT_Smx_N
     -formula Nitro -1 Smx 1
 # k13
       -parms     $K13        $

DES_Smx
     -formula   Smx 1  Des -1 
       #  	 k14 (  mol SMX/mol time)
       -parms     $K14        $  $K_DOC2           $

Smx_undet
-formula Smx -1 Undet +1
       -parms    $K15                    $
Undet_Smx
-formula Smx +1 Undet -1
       -parms   $K16           $


RATES

##############################OC release##############################
Som
-start
01 rate= parm(1)
10 moles = rate*time 
15 put(rate,01)
20 SAVE moles
-end

 Doc_r
-start
01 mDocr       = tot("Docr")
03 rate       = parm(1)*mDocr 
10 moles      = rate *time
15 put(rate,02)
16 put(monod_DOCr,800)
20 SAVE moles
-end

##############################Nitrogen species from DOC anoxic##############################
##############################Denitrification##############################
    Doc_Degradation_NITu
-start
40 rate_NO3   = parm(1)*tot("N(5)")*tot("Doc")
50 put(rate_NO3, 13)
60 moles 	  = (rate_NO3) *time
70 SAVE moles
-end

    Doc_Degradation_NITdos
-start
10 mNO3  	  = tot("N(5)")
40 inhib_NO3   = parm(2)/(parm(2)+mNO3)
50 rate_NO2   = (parm(1)*tot("Nit")*tot("Doc")*inhib_NO3)
55 put(rate_NO2, 14)
60 moles 	  = (rate_NO2) *time
70 SAVE moles
-end

######### SMX biotransformation oxygen ########################

Smx_Ammet
-start
    09 mDoc         = tot("Doc")
    10 inhib_DOC    = (parm(2)/(parm(2)+mDoc))
    15 rate         = parm(1)*tot("Smx")*inhib_DOC
	20 moles        = rate*time
    35 put(rate, 18)
	40 SAVE moles
-end

Smx_DES_O
-start
10 mSmx  	    = tot("Smx")
35 mDoc        = tot('Doc')
52  rate_SmxDes  = (parm(1)*mSmx* mDoc)
55 put(rate_SmxDes, 191)
60 moles 	  = (rate_SmxDes) *time  
70 SAVE moles
-end



Smx_DES_N
-start
10 rate= parm(1)* mol("H(Nit)")*tot("Doc")*tot("Smx")
11 put(rate, 19)
20 moles 	  = rate *time  
70 SAVE moles

-end

DES_Smx
-start
    01 mDes         = tot("Des")
    02 mDOC 	    = tot("Doc")
    03 inhib_Doc    = parm(2)/(parm(2)+mDOC)
    #04 if mNO3>=1e-4 then goto 30
    10 rate = parm(1)* mDes *inhib_Doc 
    15 put(rate, 32)
	20 moles=rate*time
	30 SAVE moles
-end

NIT_Smx_N
-start
    10 rate = (parm(1)*tot("Nitro"))
    15 put(rate, 31)
	20 moles=rate*time
	30 SAVE moles
-end

Des_NIT_N
-start
    #10 HNO3= mol('H+')
    11 HNO3= (mol('H+'))
    20 rate= parm(1)*tot("Des")*HNO3
    25 put(rate, 210)
	30 moles=rate*time
	40 SAVE moles
-end

Smx_NIT
-start
	10 rate= parm(1)* mol("H(Nit)")*mol("H(Nit)")*tot("Smx")
	20 moles=rate*time
    35 put(rate, 20)
	40 SAVE moles
-end


Smx_undet
-start
    01 mNO3  	  = tot("N(+5)")
    02 mDoc         = tot("Doc")
	10 rate= parm(1)* tot("Smx")*mDoc
	20 moles=rate*time
    35 put(rate, 990)
	40 SAVE moles
-end
Undet_Smx
-start
	10 rate= parm(1)* tot("Undet")
	20 moles=rate*time
    35 put(rate, 999)
	40 SAVE moles
-end

 
SELECTED_OUTPUT 
	-file output/Results.sel
	#-distance true
	-time true
	-reset false

USER_PUNCH
#Time	Doc	Docr	O2	Amonia	NO3-	NO2-	HNO2	DIC	N2	Fe2	rateSom	Docr	Nit1	Nit2	Docox	Desnit1	Desnit2	rateFe	pH	pe	BalN	BalC	Goet
-headings Time Doc	Docr	O2	Amonia	NO3-	NO2-	HNO2	DIC	N2	Fe2	Som	Docr	Nit1	Nit2	Docox	Desnit1	Desnit2	rateFe	pH	pe	BalN	BalC	Goet Smx Sdz Smz Ammet DES rate_Smz rate_Sdz rate_Ammet rateDes_N Nit rateNit rateDES_NIT_O HNO3  rateNIT_Smx_O2  rateNIT_Smx_N rateDES_Smx_O2 rateDES_SMX_O2 rate_Ammet_CO2 TOTAL_SMX rate_Smx_DES_O  CO2 14C rateDES_NIT_N monod_DOCr Undetected rate_undet rateSmx_othermetabolites Alcohol Smxsorb Ammetsorb Nitrosorb Dessorb undet_smx 
	-start
10 	PUNCH TOTAL_TIME
20  PUNCH tot("Doc") tot("Docr")   MOL("O2")  tot("Amonia")  tot("N(5)")  tot("Nit")  mol("H(Nit)")  tot("C(4)") tot("N(0)") 
30  TOTAL_N = tot("N(5)")+tot("Amonia")+tot("Nit")+tot("N(0)")+tot("N(3)")
40  TOTAL_C = tot("C(4)")+tot("Doc")+tot("Docr")+kin("Som")+tot("C(-4)")
# 01 Som 02 Doc_r 10 Nit1 11 Nit2 12 Doc_Degradation_OX  13 Doc_Degradation_NITu 14 Doc_Degradation_NITdos 15 Doc_Degradation_Iron
50  PUNCH tot("Fe(2)") get(01) get(02) get(10) get(11) get(12) get(13) get(14) get(15)
60  PUNCH - la("H+") 
70  PUNCH - la("e-") 
80  PUNCH TOTAL_N TOTAL_C  equi("Goethite") 

90 PUNCH tot('Smx')  tot('Sdz') tot('Smz') tot("Ammet") tot('Des') get(16) get(17) get(18) get(19) tot("Nitro") get(20) get(21) 
100 HNO3= (mol("NO3-")*mol("H+"))/2.4e-4
110 PUNCH HNO3  #= mol('H+')
# get 30> NIT_Smx_O2 get (31) NIT_Smx_N 32 DES_Smx_O2 33 DES_Smx_N 34 rateAMM_CO2
120 PUNCH get (30) get (31) get(32) get(33) get(34)
130 TOTAL_SMX = tot('Smx')+ tot("Ammet")+ tot('Des')+tot("Nitro")
140 PUNCH TOTAL_SMX
# get(191) rate_Smx_DES_O get(210) rateDES_NIT_N
150 PUNCH get(191) MOL("CO2") TOT("Label") get(210) get(800) tot('Undet') get(990) get(900) TOT('Alc') MOL('SmxSediment') MOL('AmmetSediment') MOL('NitroSediment') MOL('DesSediment') get(999) 
  	-end

















