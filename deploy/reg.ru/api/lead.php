<?php
// Soul of Home: приём заявок с сайта → сообщение мастеру через Telegram-бота @SoulHomeRuBot.
// Токен бота НЕ хранится здесь: он лежит в soh-config.php (см. config.example.php).
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');

function out($code, $data) { http_response_code($code); echo json_encode($data, JSON_UNESCAPED_UNICODE); exit; }

if ($_SERVER['REQUEST_METHOD'] !== 'POST') out(405, ['ok' => false, 'error' => 'method']);

// конфиг: сначала вне папки сайта (надёжнее), потом рядом (закрыт .htaccess)
$cfg = null;
foreach ([dirname(__DIR__, 2) . '/soh-config.php', __DIR__ . '/config.php'] as $p) {
  if (is_file($p)) { $cfg = require $p; break; }
}
if (!is_array($cfg) || empty($cfg['bot_token']) || empty($cfg['admin_chat_id'])) out(503, ['ok' => false, 'error' => 'not_configured']);

// принимаем заявки только со своего сайта
$host = strtolower(preg_replace('/:\d+$/', '', $_SERVER['HTTP_HOST'] ?? ''));
$origin = $_SERVER['HTTP_ORIGIN'] ?? ($_SERVER['HTTP_REFERER'] ?? '');
$oh = strtolower((string) parse_url($origin, PHP_URL_HOST));
if ($origin && preg_replace('/^www\./', '', $oh) !== preg_replace('/^www\./', '', $host)) out(403, ['ok' => false, 'error' => 'origin']);

$raw = file_get_contents('php://input', false, null, 0, 8192);
$in = json_decode($raw, true);
if (!is_array($in)) out(400, ['ok' => false, 'error' => 'json']);
if (!empty($in['website'])) out(200, ['ok' => true, 'id' => 'X']);   // ловушка для спам-ботов

// не больше 5 заявок с одного IP за 10 минут
$ip = $_SERVER['REMOTE_ADDR'] ?? '0';
$rl = sys_get_temp_dir() . '/soh-rl-' . md5($ip);
$hits = array_filter(is_file($rl) ? (array) json_decode((string) @file_get_contents($rl), true) : [], fn($t) => $t > time() - 600);
if (count($hits) >= 5) out(429, ['ok' => false, 'error' => 'rate']);
$hits[] = time(); @file_put_contents($rl, json_encode(array_values($hits)));

function clean($v, $n = 200) { $v = trim(preg_replace('/\s+/u', ' ', (string) $v)); return mb_substr(strip_tags($v), 0, $n); }

$forms = [
  'office' => ['Заявка «Офис к Новому году» (чек-лист)', ['name' => 'Имя', 'company' => 'Компания', 'phone' => 'Телефон', 'email' => 'E-mail', 'date' => 'Дата корпоратива', 'zone' => 'Что оформить']],
  'course' => ['Заявка на обучение', ['course' => 'Программа']],
];
$form = $in['form'] ?? '';
if (!isset($forms[$form])) out(400, ['ok' => false, 'error' => 'form']);
[$title, $fields] = $forms[$form];

$f = [];
foreach ($fields as $k => $label) $f[$k] = clean($in[$k] ?? '');
if ($form === 'office') {
  if ($f['name'] === '' || strlen(preg_replace('/\D/', '', $f['phone'])) < 10) out(422, ['ok' => false, 'error' => 'fields']);
  if ($f['email'] !== '' && !filter_var($f['email'], FILTER_VALIDATE_EMAIL)) out(422, ['ok' => false, 'error' => 'email']);
}
if ($form === 'course' && $f['course'] === '') out(422, ['ok' => false, 'error' => 'fields']);

$id = strtoupper(substr(base_convert((string) random_int(1679616, 60466175), 10, 36), 0, 5));   // например K7F3Q
$lines = ["📝 $title · №$id", ''];
foreach ($fields as $k => $label) if ($f[$k] !== '') $lines[] = "$label: {$f[$k]}";
$page = clean($in['page'] ?? '', 120);
$lines[] = '';
$lines[] = 'Страница: ' . ($page ?: $host);
$lines[] = 'Если клиент нажмёт кнопку Telegram на сайте, бот пришлёт «Клиент по заявке №' . $id . ' открыл бота» — отвечайте ему ответом на то сообщение.';
$text = implode("\n", $lines);

$ch = curl_init(($cfg['api_base'] ?? 'https://api.telegram.org') . '/bot' . $cfg['bot_token'] . '/sendMessage');
curl_setopt_array($ch, [CURLOPT_POST => true, CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 10,
  CURLOPT_POSTFIELDS => ['chat_id' => $cfg['admin_chat_id'], 'text' => $text, 'disable_web_page_preview' => 'true']]);
$res = curl_exec($ch); $code = curl_getinfo($ch, CURLINFO_HTTP_CODE); curl_close($ch);
if ($code !== 200) { error_log("soh lead: telegram $code $res"); out(502, ['ok' => false, 'error' => 'telegram']); }
out(200, ['ok' => true, 'id' => $id]);
