//
// ============================================================
// ATLAS.IA
// ATLAS MINI V1
// Mascote físico paramétrico para impressão 3D
//
// Impressora alvo: Bambu Lab A1
// Bico: 0.4 mm
// Escala inicial: ~100 mm
// ============================================================
//

$fn = 64;


// ============================================================
// PARÂMETROS GERAIS
// ============================================================

atlas_scale = 1.0;

// Visualização
show_head     = true;
show_face     = true;
show_ears     = true;
show_cap      = true;
show_body     = true;
show_arms     = true;
show_hands    = true;
show_legs     = true;
show_feet     = true;
show_logo     = true;


// ============================================================
// CORES DE VISUALIZAÇÃO
// ============================================================

WHITE  = [0.92, 0.92, 0.90];
BLACK  = [0.025, 0.030, 0.035];
YELLOW = [1.00, 0.62, 0.03];
BLUE   = [0.00, 0.55, 1.00];
RED    = [0.85, 0.03, 0.03];


// ============================================================
// FUNÇÕES AUXILIARES
// ============================================================

module rounded_box(size=[10,10,10], r=2) {

    hull() {

        for (x=[-1,1])
        for (y=[-1,1])
        for (z=[-1,1])

            translate([
                x*(size[0]/2-r),
                y*(size[1]/2-r),
                z*(size[2]/2-r)
            ])

            sphere(r=r);
    }
}


// ============================================================
// PÉ
// ============================================================

module foot(side=1) {

    translate([
        side*11,
        2,
        7
    ])

    scale([1.25,1.55,0.75])

    rounded_box(
        [14,15,10],
        3
    );
}


// ============================================================
// PERNA
// ============================================================

module leg(side=1) {

    // perna principal
    translate([
        side*10,
        0,
        20
    ])

    scale([0.85,0.85,1.2])

    rounded_box(
        [10,10,16],
        3
    );


    // joelho
    color(YELLOW)

    translate([
        side*10,
        -5,
        22
    ])

    rotate([90,0,0])

    cylinder(
        h=2.5,
        d=7,
        center=true
    );
}


// ============================================================
// CORPO
// ============================================================

module torso() {

    // corpo principal

    color(WHITE)

    translate([0,0,43])

    scale([1.1,0.8,1])

    rounded_box(
        [31,22,27],
        6
    );


    // peitoral amarelo

    color(YELLOW)

    translate([0,-11.3,45])

    scale([1,0.35,1])

    rounded_box(
        [25,4,17],
        2
    );


    // parte inferior

    color(BLACK)

    translate([0,0,31])

    rounded_box(
        [19,16,7],
        2
    );
}


// ============================================================
// LOGO ATLAS SIMPLIFICADO
// ============================================================

module atlas_logo() {

    color(BLUE)

    translate([0,-13.7,43])

    rotate([90,0,0])

    linear_extrude(height=1.2)

    polygon(
        points=[
            [-5,-4],
            [0,5],
            [5,-4],
            [2,-4],
            [0,0],
            [-2,-4]
        ]
    );
}


// ============================================================
// BRAÇO
// ============================================================

module arm(side=1) {

    // ombro

    color(YELLOW)

    translate([
        side*20,
        0,
        48
    ])

    sphere(d=12);


    // braço

    color(WHITE)

    translate([
        side*22,
        0,
        38
    ])

    rotate([
        0,
        side*10,
        0
    ])

    rounded_box(
        [9,10,16],
        3
    );


    // articulação do cotovelo

    color(BLACK)

    translate([
        side*23,
        0,
        31
    ])

    sphere(d=7);
}


// ============================================================
// MÃO
// ============================================================

module hand(side=1) {

    color(BLACK)

    translate([
        side*24,
        -1,
        26
    ])

    scale([0.85,0.75,1])

    sphere(d=9);
}


// ============================================================
// CABEÇA
// ============================================================

module head() {

    color(WHITE)

    translate([0,0,75])

    scale([
        1.35,
        0.90,
        1
    ])

    rounded_box(
        [36,28,29],
        8
    );
}


// ============================================================
// VISOR
// ============================================================

module visor() {

    color(BLACK)

    translate([
        0,
        -15.1,
        75
    ])

    scale([
        1.3,
        0.25,
        0.78
    ])

    rounded_box(
        [31,5,24],
        5
    );


    // OLHO ESQUERDO

    color(BLUE)

    translate([
        -9,
        -17.8,
        78
    ])

    rotate([90,0,0])

    scale([1.5,1,1])

    difference() {

        cylinder(
            h=1,
            d=7,
            center=true
        );

        translate([0,-2,0])

        cube(
            [10,5,3],
            center=true
        );
    }


    // OLHO DIREITO

    color(BLUE)

    translate([
        9,
        -17.8,
        78
    ])

    rotate([90,0,0])

    scale([1.5,1,1])

    difference() {

        cylinder(
            h=1,
            d=7,
            center=true
        );

        translate([0,-2,0])

        cube(
            [10,5,3],
            center=true
        );
    }


    // BOCA

    color(BLUE)

    translate([
        0,
        -18,
        69
    ])

    rotate([90,0,0])

    difference() {

        cylinder(
            h=1,
            d=8,
            center=true
        );

        translate([0,3,0])

        cube(
            [12,7,3],
            center=true
        );
    }
}


// ============================================================
// FONES
// ============================================================

module ears() {

    for(side=[-1,1]) {

        // estrutura externa

        color(YELLOW)

        translate([
            side*27,
            0,
            76
        ])

        rotate([0,90,0])

        cylinder(
            h=5,
            d=15,
            center=true
        );


        // centro preto

        color(BLACK)

        translate([
            side*29.7,
            0,
            76
        ])

        rotate([0,90,0])

        cylinder(
            h=1.5,
            d=11,
            center=true
        );


        // núcleo azul

        color(BLUE)

        translate([
            side*30.6,
            0,
            76
        ])

        rotate([0,90,0])

        cylinder(
            h=0.8,
            d=6,
            center=true
        );
    }
}


// ============================================================
// BONÉ
// ============================================================

module cap() {

    // copa

    color(BLACK)

    intersection() {

        translate([0,0,91])

        scale([
            1.25,
            0.85,
            0.55
        ])

        sphere(d=37);


        translate([0,0,94])

        cube(
            [60,60,15],
            center=true
        );
    }


    // aba

    color(BLACK)

    translate([
        0,
        -16,
        90
    ])

    scale([
        1.7,
        1,
        0.25
    ])

    sphere(d=16);


    // botão superior

    color(RED)

    translate([0,0,101])

    sphere(d=3);
}


// ============================================================
// PESCOÇO
// ============================================================

module neck() {

    color(BLACK)

    translate([0,0,59])

    cylinder(
        h=7,
        d=12,
        center=true
    );
}


// ============================================================
// ATLAS MINI COMPLETO
// ============================================================

module atlas_mini() {

    scale([atlas_scale,atlas_scale,atlas_scale]) {

        if(show_feet) {

            color(WHITE) {

                foot(-1);
                foot(1);
            }
        }


        if(show_legs) {

            color(WHITE) {

                leg(-1);
                leg(1);
            }
        }


        if(show_body)

            torso();


        neck();


        if(show_logo)

            atlas_logo();


        if(show_arms) {

            arm(-1);
            arm(1);
        }


        if(show_hands) {

            hand(-1);
            hand(1);
        }


        if(show_head)

            head();


        if(show_face)

            visor();


        if(show_ears)

            ears();


        if(show_cap)

            cap();
    }
}


// ============================================================
// GERAR ATLAS
// ============================================================

atlas_mini();