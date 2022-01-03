-- Drop all old
-- DROP TABLE IF EXISTS LECTURE
-- DROP TABLE IF EXISTS CHAPTER;
-- DROP TABLE IF EXISTS QUESTIONS;
-- DROP TABLE IF EXISTS HIERARCHY;
-- DROP TABLE IF EXISTS QUESTION_RESULTS;
-- DROP TABLE IF EXISTS CHAPTER_RESULTS;

-- Create tables
CREATE TABLE IF NOT EXISTS LECTURE
(
    n_lecture_id   SERIAL UNIQUE NOT NULL,
    s_lecture       VARCHAR(128)  NOT NULL,
    s_content       VARCHAR(100000)   NOT NULL,
    PRIMARY KEY (n_lecture_id)
);

CREATE TABLE IF NOT EXISTS CHAPTER
(
    n_chapter_id   SERIAL UNIQUE NOT NULL,
    s_lecture       VARCHAR(128)  NOT NULL,
    s_chapter       VARCHAR(128)   NOT NULL,
    s_content       VARCHAR(10000)   NOT NULL,
    PRIMARY KEY (n_chapter_id)
);

CREATE TABLE IF NOT EXISTS QUESTIONS
(
    n_question_id   SERIAL UNIQUE NOT NULL,
    n_chapter_id    INT NOT NULL,
    s_question      VARCHAR(128)   NOT NULL,
    s_answer        VARCHAR(128)   NOT NULL,
    PRIMARY KEY (n_question_id),
    FOREIGN KEY (n_chapter_id) REFERENCES CHAPTER (n_chapter_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS HIERARCHY
(
  n_super_chapter_id    INT NOT NULL,
  n_sub_chapter_id      INT NOT NULL,
  FOREIGN KEY (n_super_chapter_id) REFERENCES CHAPTER (n_chapter_id) ON DELETE CASCADE,
  FOREIGN KEY (n_sub_chapter_id) REFERENCES CHAPTER (n_chapter_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS QUESTION_RESULTS
(
   n_question_id     INT NOT NULL,
   n_solved         INT NOT NULL, --0=FALSE, 1=TRUE
   FOREIGN KEY (n_question_id) REFERENCES QUESTIONS (n_question_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS CHAPTER_RESULTS
(
   n_chapter_id     INT NOT NULL,
   n_qualificated   INT NOT NULL, --0=FALSE, 1=TRUE
   n_solved         INT NOT NULL, --0=FALSE, 1=TRUE
   FOREIGN KEY (n_chapter_id) REFERENCES CHAPTER (n_chapter_id) ON DELETE CASCADE
);

-- Fill tables
INSERT INTO LECTURE(s_lecture, s_content)
VALUES ('Databases I', '<p>Content of Database I</p>');

INSERT INTO CHAPTER(s_lecture, s_chapter, s_content)
VALUES ('Databases I', '1.', 'Content of Chapter 1.'),
       ('Databases I', '1.1.', 'Content of Chapter 1.1.'),
       ('Databases I', '1.2.', 'Content of Chapter 1.2.');

INSERT INTO QUESTIONS(n_chapter_id, s_question, s_answer)
VALUES (1, 'Question 1 to Chapter 1. of Databases I', 'Answer 1 to Chapter 1. of Databases I'),
       (1, 'Question 2 to Chapter 1. of Databases I', 'Answer 2 to Chapter 1. of Databases I'),
       (2, 'Question 1 to Chapter 1.1 of Databases I', 'Answer 1 to Chapter 1.1 of Databases I'),
       (2, 'Question 2 to Chapter 1.1 of Databases I', 'Answer 2 to Chapter 1.1 of Databases I'),
       (3, 'Question 1 to Chapter 1.2 of Databases I', 'Answer 1 to Chapter 1.2 of Databases I'),
       (3, 'Question 2 to Chapter 1.2 of Databases I', 'Answer 2 to Chapter 1.2 of Databases I');

INSERT INTO HIERARCHY(n_super_chapter_id, n_sub_chapter_id)
VALUES (1, 2),
       (1,3);

INSERT INTO QUESTION_RESULTS(n_question_id, n_solved)
VALUES (1, 0),
       (2, 0),
       (3, 0),
       (4, 0),
       (5, 0),
       (6, 0);


INSERT INTO CHAPTER_RESULTS(n_chapter_id, n_qualificated, n_solved)
VALUES (1, 1, 0),
       (2, 0, 0),
       (3, 0, 0);

-- Create views
CREATE VIEW Result_Overview AS
SELECT C.s_lecture AS Lecture, ROUND(AVG(CR.n_solved),2) AS Completed
FROM CHAPTER_RESULTS AS CR LEFT JOIN CHAPTER  AS C ON CR.n_chapter_id = C.n_chapter_id
GROUP BY C.s_lecture;


-- Create procedures
create or replace procedure add_content(
    s_lecture       VARCHAR(128),
    s_chapter       VARCHAR(128),
    s_content       VARCHAR(10000)
)
-- without addresses
    language plpgsql
AS
$$
DECLARE
    chapter_id      INT;

BEGIN
    INSERT INTO CHAPTER(s_lecture, s_chapter, s_content)
    VALUES (s_lecture, s_chapter, s_content)
    RETURNING n_chapter_id INTO chapter_id;

    IF s_lecture = s_chapter
    THEN
        INSERT INTO CHAPTER_RESULTS(n_chapter_id, n_qualificated, n_solved)
        VALUES (chapter_id, 1, 0);
    ELSE
       INSERT INTO CHAPTER_RESULTS(n_chapter_id, n_qualificated, n_solved)
        VALUES (chapter_id, 0, 0);

    END IF;

END;
$$
;


create or replace procedure add_hierarchy(
    s_lecture_txt       VARCHAR(128),
    s_super_chapter     VARCHAR(128),
    s_sub_chapter       VARCHAR(128)
)

    language plpgsql
AS
$$
DECLARE
    super_chapter_id      INT;
    sub_chapter_id        INT;
BEGIN
    super_chapter_id := (SELECT n_chapter_id FROM CHAPTER WHERE s_chapter = s_super_chapter AND s_lecture = s_lecture_txt);
    sub_chapter_id := (SELECT n_chapter_id FROM CHAPTER WHERE s_chapter = s_sub_chapter AND s_lecture = s_lecture_txt);

    INSERT INTO HIERARCHY(n_super_chapter_id, n_sub_chapter_id)
    VALUES (super_chapter_id, sub_chapter_id);
END;
$$
;


create or replace procedure add_lecture(
    s_lecture_txt       VARCHAR(128),
    s_lecture_content   VARCHAR(100000)
)

    language plpgsql
AS
$$
DECLARE
    lecture_id      INT;

BEGIN

    INSERT INTO LECTURE(s_lecture, s_content)
    VALUES (s_lecture_txt, s_lecture_content)
    RETURNING n_lecture_id INTO lecture_id;
END
$$
;


