#include "source1.h"
#include <iostream>

int fDoWhile(void)
{
    //$ Init i with 0
    int i=0;
    //$ Init value with 0
    int value=0;

    do
    {
        //$ Add 2 power i
        value += 2<<i;
        //$ Increment i
        i++;
    } while (i<10); // Flowgen will take C-condition

    //$ Set i to 0
    i=0;
    do
    {
        //$ subtract 2 power i
        value -= 2<<i;
        //$ Increment i
        i++;
    //$ [ max i]
    } while (i<10); // Flowgen will take condition from comment

    //$ Return value
    return value;

}

int fWhile(void)
{
    //$ Init i with 0
    int i=0;
    //$ Init value with 0
    int value=0;

    while (i<10) // Flowgen will take C-condition
    {
        //$ Add 2 power i
        value += 2<<i;
        //$ Increment i
        i++;
    };

    //$ Set i to 0
    i=0;
    //$ [ max i]
    while (i<10) // Flowgen will take condition from comment
    {
        //$ subtract 2 power i
        value -= 2<<i;
        //$ Increment i
        i++;
    };

    //$ Return value
    return value;

}

int fFor(void)
{
    int i;
    //$ Init value with 0
    int value=0;

    for (i=0; i<10; i++)  // Flowgen will take initializers, condition and increment from C
    {
        //$ Add 2 power i
        value += 2<<i;
    };

    //$ [ Start with zero; Index less than ten; Increment index]
    for (i=0; i<10; i++) // Flowgen will take initializers, condition and increment from Comment
    {
        //$ subtract 2 power i
        value -= 2<<i;
    };

    //$ [ Index less than ten]
    for (i=0; i<10; i++)  // Flowgen will take condition from C, initializers and increment from C
    {
        //$ Add 2 power i
        value += 2<<i;
    };

    //$ [ Start with zero; ; ]
    for (i=0; i<10; i++) // Flowgen will take initializers, condition and increment from Comment
    {
        //$ subtract 2 power i
        value -= 2<<i;
    };

    //$ Return value
    return value;

}



int main()
{
    int control_flag=0;
    int value;

    //$ ask user whether to proceed
    std::cin >> control_flag;

    if (control_flag==1){
        //$ call shower
        //pointer to the object VINCIA
        VINCIA* vinciaOBJ = new VINCIA();
        vinciaOBJ->shower(); //$
    }

    switch( control_flag )
    {
        //$ [First case]
    case 0:
        //$ Call routine for do - while test
        value=fDoWhile(); //$

        break;

        //$ [Second case]
    case 1:
        //$ Call routine for while - do test
        value=fWhile(); //$
        break;

        //$ [Other cases]
    default:
        //$ Call for routine - for test
        value=fFor(); //$
        break;
    }

    return 0;
}
