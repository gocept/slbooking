INSERT INTO user (username, mail, password)
VALUES
  ('a', 'mail', 'pbkdf2:sha256:50000$TCI4GzcX$0de171a4f4dac32e3364c7ddc7c14
  	f3e2fa61f2d17574483f7ffbb431b4acb2f'),
  ('a2', 'mail2', 'pbkdf2:sha256:50000$kJPKsz6N$d2d4784f1b030a9761f5ccaeeaca
  	413f27f2ecb76d6168407af962ddce849f79');

INSERT INTO admin (adminname, password)
VALUES
  ('test', 'pbkdf2:sha256:50000$TCI4GzcX$0de171a4f4dac32e3364c7ddc7c14f3e2fa61f
  	2d17574483f7ffbb431b4acb2f'),
  ('other', 'pbkdf2:sha256:50000$kJPKsz6N$d2d4784f1b030a9761f5ccaeeaca413f27f2
  	ecb76d6168407af962ddce849f79');
