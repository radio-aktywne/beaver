-- CreateEnum
CREATE TYPE "event_type" AS ENUM('live', 'replay', 'prerecorded');

-- CreateTable
CREATE TABLE
  "shows" (
    "id" UUID NOT NULL,
    "title" STRING(255) NOT NULL,
    "description" STRING(16384),
    CONSTRAINT "shows_pkey" PRIMARY KEY ("id")
  );

-- CreateTable
CREATE TABLE
  "events" (
    "id" UUID NOT NULL,
    "type" "event_type" NOT NULL,
    "show_id" UUID NOT NULL,
    CONSTRAINT "events_pkey" PRIMARY KEY ("id")
  );

-- CreateIndex
CREATE UNIQUE INDEX "title_unique" ON "shows" ("title");

-- AddForeignKey
ALTER TABLE "events"
ADD CONSTRAINT "show_id_fkey" FOREIGN KEY ("show_id") REFERENCES "shows" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;
