CREATE TABLE "movimientos" (
	"id"	INTEGER,
	"fecha"	TEXT NOT NULL,
	"hora"	TEXT NOT NULL,
	"monedafrom"	INTEGER NOT NULL,
	"cantidadfrom"	REAL NOT NULL,
	"monedato"	INTEGER NOT NULL,
	"cantidadto"	REAL NOT NULL,
	"conversion"	REAL,
	PRIMARY KEY("id" AUTOINCREMENT)
)