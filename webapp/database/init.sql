-- Drop all old
DROP VIEW IF EXISTS CONTENT;
DROP VIEW IF EXISTS QUESTIONS;

-- Create tables
CREATE TABLE CONTENT
(
    n_chapter_id   SERIAL UNIQUE NOT NULL,
    s_lecture       VARCHAR(128)  NOT NULL,
    s_chapter_nr    VARCHAR(128)   NOT NULL,
    s_content       VARCHAR(10000)   NOT NULL,
    PRIMARY KEY (n_chapter_id)
);

CREATE TABLE QUESTIONS
(
    n_question_id   SERIAL UNIQUE NOT NULL,
    n_chapter_id    INT NOT NULL,
    s_question      VARCHAR(128)   NOT NULL,
    PRIMARY KEY (n_question_id),
    FOREIGN KEY (n_chapter_id) REFERENCES CONTENT (n_chapter_id) ON DELETE CASCADE
);

-- Fill tables
INSERT INTO CONTENT(s_lecture, s_chapter_nr, s_content)
VALUES ('Databases I', '1.', 'Content of Chapter 1.'),
       ('Databases I', '1.1.', 'Content of Chapter 1.1.'),
       ('Databases I', '1.2.', 'Content of Chapter 1.2.');

INSERT INTO QUESTIONS(n_chapter_id, s_question)
VALUES (1, 'Question to Chapter 1. of Databases I'),
       (2, 'Question to Chapter 1.1 of Databases I'),
       (3, 'Question to Chapter 1.2 of Databases I'),
