-- Drop all old
-- DROP TABLE IF EXISTS CONTENT;
-- DROP TABLE IF EXISTS QUESTIONS;
-- DROP TABLE IF EXISTS HIERARCHY;
-- DROP TABLE IF EXISTS QUESTION_RESULTS;
-- DROP TABLE IF EXISTS CHAPTER_RESULTS;

-- Create tables
CREATE TABLE IF NOT EXISTS CONTENT
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
    b_solved        BOOLEAN NOT NULL,
    PRIMARY KEY (n_question_id),
    FOREIGN KEY (n_chapter_id) REFERENCES CONTENT (n_chapter_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS HIERARCHY
(
  n_super_chapter_id    INT NOT NULL,
  n_sub_chapter_id      INT NOT NULL,
  FOREIGN KEY (n_super_chapter_id) REFERENCES CONTENT (n_chapter_id) ON DELETE CASCADE,
  FOREIGN KEY (n_sub_chapter_id) REFERENCES CONTENT (n_chapter_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS QUESTION_RESULTS
(
   n_question_id     INT NOT NULL,
   b_solved         BOOLEAN NOT NULL,
   FOREIGN KEY (n_question_id) REFERENCES QUESTIONS (n_question_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS CHAPTER_RESULTS
(
   n_chapter_id     INT NOT NULL,
   b_qualificated   BOOLEAN NOT NULL,
   b_solved         BOOLEAN NOT NULL,
   FOREIGN KEY (n_chapter_id) REFERENCES CONTENT (n_chapter_id) ON DELETE CASCADE
);

-- Fill tables
INSERT INTO CONTENT(s_lecture, s_chapter, s_content)
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

INSERT INTO QUESTION_RESULTS(n_chapter_id, b_solved)
VALUES (1, FALSE),
       (2, FALSE),
       (3, FALSE),
       (4, FALSE),
       (5, FALSE),
       (6, FALSE);


INSERT INTO CHAPTER_RESULTS(n_chapter_id, b_qualificated, b_solved)
VALUES (1, TRUE, FALSE),
       (2, FALSE, FALSE),
       (3, FALSE, FALSE);
