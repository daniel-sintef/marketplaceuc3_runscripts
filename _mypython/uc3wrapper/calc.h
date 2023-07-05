#include "udf.h"
#include "math.h"

#define R 8.314											/* J/m/K */

/* Catalyst properties*/
#define A0 66.5							/* ***USER INPUT*** Initial active surface area (m2/g active material)*/
#define X_pd 0.05						/* ***USER INPUT*** Mass fraction of active material */

/* Set reaction rate parameters*/
#define k0 10000.0						/* ***USER INPUT*** Pre-exponential factor*/
#define Ea 100000.0						/* ***USER INPUT*** Activation energy (J/mol) */

/* Support particle properties*/
#define por_cat 0.14					/* ***USER INPUT*** Catalyst support macroporosity*/
#define tort 3.0						/* ***USER INPUT*** Macropore tortuosity */
#define rp 271.0						/* ***USER INPUT*** Macropore average radius (nm)*/
