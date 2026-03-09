--liquibase formatted sql

--changeset author:rdube26:insert_ques_risk_ctgy
INSERT into ques_risk_ctgy values ('H','High Risk');
INSERT into ques_risk_ctgy values ('M','Medium Risk');
INSERT into ques_risk_ctgy values ('L','Low Risk');
INSERT into ques_risk_ctgy values ('N','Nominal Risk');
INSERT into ques_risk_ctgy values ('NA','Not Applicable');
