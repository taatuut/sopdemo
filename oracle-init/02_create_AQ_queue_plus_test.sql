-- In Containers oracle19c Exec run command:
-- sqlplus / as sysdb

-- Create an AQ demo queue (RAW payload) + test
ALTER SESSION SET CONTAINER = ORCLPDB1;
ALTER SESSION SET CURRENT_SCHEMA = testuser;

-- Create demo user
CREATE USER aqdemo IDENTIFIED BY "AQdemo#123"
  DEFAULT TABLESPACE users
  TEMPORARY TABLESPACE temp
  QUOTA UNLIMITED ON users;

GRANT CREATE SESSION, CREATE TABLE, CREATE PROCEDURE TO aqdemo;

-- AQ privileges
GRANT AQ_ADMINISTRATOR_ROLE TO aqdemo;
GRANT AQ_USER_ROLE TO aqdemo;

GRANT EXECUTE ON SYS.DBMS_AQ TO aqdemo;
GRANT EXECUTE ON SYS.DBMS_AQADM TO aqdemo;

-- Should return 'User created' followed by five 'Grant succeeded' messages.

-- Now connect as AQDEMO:
CONNECT aqdemo/"AQdemo#123"@//localhost:1521/ORCLPDB1

-- Should return 'Connected.'

-- Create and start a RAW queue:
BEGIN
  DBMS_AQADM.CREATE_QUEUE_TABLE(
    queue_table        => 'AQDEMO_QTAB',
    queue_payload_type => 'RAW'
  );

  DBMS_AQADM.CREATE_QUEUE(
    queue_name  => 'AQDEMO_QUEUE',
    queue_table => 'AQDEMO_QTAB'
  );

  DBMS_AQADM.START_QUEUE(
    queue_name => 'AQDEMO_QUEUE'
  );
END;
/
-- Should return 'PL/SQL procedure successfully completed.'

-- Enable server output if you want to see the msgid:
SET SERVEROUTPUT ON

-- Enqueue one message (publish)
DECLARE
  enqopt    DBMS_AQ.ENQUEUE_OPTIONS_T;
  msgprop   DBMS_AQ.MESSAGE_PROPERTIES_T;
  msgid     RAW(16);
  v_payload VARCHAR2(200);
BEGIN
  v_payload :=
      'hello aq, your uuid=' || RAWTOHEX(SYS_GUID());

  DBMS_AQ.ENQUEUE(
    queue_name         => 'AQDEMO_QUEUE',
    enqueue_options    => enqopt,
    message_properties => msgprop,
    payload            => UTL_RAW.CAST_TO_RAW(v_payload),
    msgid              => msgid
  );
  COMMIT;
  DBMS_OUTPUT.PUT_LINE('Enqueued msgid=' || RAWTOHEX(msgid));
  DBMS_OUTPUT.PUT_LINE(v_payload);
END;
/

-- Should return something like 'Enqueued msgid=494D72106EA603AFE063030012AC919B' followed by 'PL/SQL procedure successfully completed.'

-- Browwse the message with dequeue, this does not consume the message.
-- In classic Oracle AQ, a successful DBMS_AQ.DEQUEUE removes the message from the queue (after COMMIT) by default.

DECLARE
  deqopt    DBMS_AQ.DEQUEUE_OPTIONS_T;
  msgprop   DBMS_AQ.MESSAGE_PROPERTIES_T;
  msgid     RAW(16);
  payload   RAW(2000);

  FUNCTION dequeue_mode_name(p_mode PLS_INTEGER) RETURN VARCHAR2 IS
  BEGIN
    CASE p_mode
      WHEN DBMS_AQ.BROWSE  THEN RETURN 'BROWSE';
      WHEN DBMS_AQ.REMOVE  THEN RETURN 'REMOVE';
      WHEN DBMS_AQ.LOCKED  THEN RETURN 'LOCKED';
      ELSE RETURN 'UNKNOWN (' || p_mode || ')';
    END CASE;
  END;
BEGIN
  deqopt.wait := DBMS_AQ.NO_WAIT;
  -- default mode is to remove like deqopt.dequeue_mode := DBMS_AQ.REMOVE;
  deqopt.dequeue_mode := DBMS_AQ.BROWSE; 

  DBMS_AQ.DEQUEUE(
    queue_name         => 'AQDEMO_QUEUE',
    dequeue_options    => deqopt,
    message_properties => msgprop,
    payload            => payload,
    msgid              => msgid
  );
  COMMIT;

  DBMS_OUTPUT.PUT_LINE('Retrieved msgid=' || RAWTOHEX(msgid));
  DBMS_OUTPUT.PUT_LINE('Payload=' || UTL_RAW.CAST_TO_VARCHAR2(payload));
  DBMS_OUTPUT.PUT_LINE('dequeue_mode=' || dequeue_mode_name(deqopt.dequeue_mode));
END;
/

-- Mode DBMS_AQ.REMOVE should return something like:
-- Dequeued msgid=494D72106EA603AFE063030012AC919B
-- Payload=hello aq
-- followed by 'PL/SQL procedure successfully completed.'

-- Quick check via dictionary view
SELECT name, queue_table, enqueue_enabled, dequeue_enabled
FROM   user_queues
ORDER  BY name;
-- Should return something like below for remove mode:

-- NAME
-- --------------------------------------------------------------------------------
-- QUEUE_TABLE
-- --------------------------------------------------------------------------------
-- ENQUEUE DEQUEUE
-- ------- -------
-- AQ$_AQDEMO_QTAB_E
-- AQDEMO_QTAB
--   NO      NO

-- AQDEMO_QUEUE
-- AQDEMO_QTAB
--   YES     YES

-- NAME
-- --------------------------------------------------------------------------------
-- QUEUE_TABLE
-- --------------------------------------------------------------------------------
-- ENQUEUE DEQUEUE
-- ------- -------

-- OPTIONAL: Clean up by stopping & dropping the queue and queue table

-- Using a single-consumer queue:
-- One message
-- One consumer
-- Dequeue (remove) = delete