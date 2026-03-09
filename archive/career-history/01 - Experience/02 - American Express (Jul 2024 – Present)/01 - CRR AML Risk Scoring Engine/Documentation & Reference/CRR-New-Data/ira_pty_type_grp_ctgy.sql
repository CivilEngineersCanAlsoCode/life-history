--liquibase formatted sql

--changeset author:rdube26:insert_ira_pty_type_grp_ctgy
INSERT INTO ira_pty_type_grp_ctgy (ira_pty_type_grp_ctgy_cd, pty_type_grp_ctgy_nm) VALUES ('GOV   ', 'Government Owned                        ');
INSERT INTO ira_pty_type_grp_ctgy (ira_pty_type_grp_ctgy_cd, pty_type_grp_ctgy_nm) VALUES ('PT    ', 'Publicly Traded                         ');
INSERT INTO ira_pty_type_grp_ctgy (ira_pty_type_grp_ctgy_cd, pty_type_grp_ctgy_nm) VALUES ('SOE   ', 'State Owned                             ');
INSERT INTO ira_pty_type_grp_ctgy (ira_pty_type_grp_ctgy_cd, pty_type_grp_ctgy_nm) VALUES ('TR    ', 'Trust                                   ');
