<?php
// SG - PS waitlist and free-trial requests.
//
// POST JSON {name, phone, product, interests[], consent, page} -> appends one row to
// <parent of this site's folder>/sgps-data/leads.csv, outside the SG - PS folder so deploys
// (which replace that folder) never touch it. A deny-all .htaccess keeps the data folder off the
// web; read it from Hostinger's File Manager (public_html/sgps-data/leads.csv on engsaber.space).
// When the deploy wrote sgps-config.php (GitHub secret SGPS_LEAD_WEBHOOK), each lead is also
// sent to that n8n webhook, which alerts the team on Telegram.

declare(strict_types=1);
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');
header('X-Content-Type-Options: nosniff');

function reply(int $code, array $body): void {
    http_response_code($code);
    echo json_encode($body, JSON_UNESCAPED_UNICODE);
    exit;
}

if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
    reply(405, ['ok' => false, 'error' => 'method']);
}
$raw = file_get_contents('php://input', false, null, 0, 8192);
$in = json_decode($raw ?: '', true);
if (!is_array($in)) {
    reply(400, ['ok' => false, 'error' => 'json']);
}

$PRODUCTS = ['SG - AI', 'SG - PR', 'SG - AE', 'SG - PS', 'general'];
$INTERESTS = [
    'graphic-design-101', 'advertising-mastery', 'ai-101', 'ai-mastery', 'ai-100x-creatives', 'not-sure',
];

$clean = static function ($v, int $max): string {
    $v = is_string($v) ? $v : '';
    $v = preg_replace('/[\x00-\x1F\x7F]+/u', ' ', $v) ?? '';
    return mb_substr(trim($v), 0, $max);
};
$name = $clean($in['name'] ?? '', 80);
$phone = preg_replace('/[^\d+]/', '', $clean($in['phone'] ?? '', 32)) ?? '';
$product = in_array($in['product'] ?? '', $PRODUCTS, true) ? $in['product'] : 'general';
$interests = array_values(array_intersect(is_array($in['interests'] ?? null) ? $in['interests'] : [], $INTERESTS));
$consent = ($in['consent'] ?? false) === true;
$page = $clean($in['page'] ?? '', 120);

$digits = preg_replace('/\D/', '', $phone) ?? '';
if ($name === '' || strlen($digits) < 8 || strlen($digits) > 15) {
    reply(422, ['ok' => false, 'error' => 'fields']);
}
if (!$consent) {
    reply(422, ['ok' => false, 'error' => 'consent']);
}

$docRoot = rtrim((string)($_SERVER['DOCUMENT_ROOT'] ?? __DIR__), '/');
$dir = dirname($docRoot) . '/sgps-data';
if (!is_dir($dir) && !mkdir($dir, 0750, true) && !is_dir($dir)) {
    reply(500, ['ok' => false, 'error' => 'storage']);
}
if (!is_file("$dir/.htaccess")) {
    file_put_contents("$dir/.htaccess", "Require all denied\n<IfModule !mod_authz_core.c>\n  Deny from all\n</IfModule>\n");
}
if (!is_file("$dir/index.html")) {
    file_put_contents("$dir/index.html", '');
}

// At most 5 requests per IP per hour.
$ip = (string)($_SERVER['HTTP_CF_CONNECTING_IP'] ?? $_SERVER['REMOTE_ADDR'] ?? '');
$bucket = "$dir/rate-" . substr(hash('sha256', $ip . date('YmdH')), 0, 16);
$hits = is_file($bucket) ? (int)file_get_contents($bucket) : 0;
if ($hits >= 5) {
    reply(429, ['ok' => false, 'error' => 'rate']);
}
file_put_contents($bucket, (string)($hits + 1));
foreach (glob("$dir/rate-*") ?: [] as $f) {
    if (filemtime($f) < time() - 7200) {
        @unlink($f);
    }
}

$file = "$dir/leads.csv";
$new = !is_file($file);
$fh = fopen($file, 'ab');
if ($fh === false || !flock($fh, LOCK_EX)) {
    reply(500, ['ok' => false, 'error' => 'storage']);
}
if ($new) {
    fwrite($fh, "\xEF\xBB\xBF"); // UTF-8 BOM so Excel shows Arabic correctly
    fputcsv($fh, ['time_utc', 'name', 'phone', 'product', 'interests', 'consent', 'page', 'user_agent']);
}
// Cells that start with = + - @ would run as formulas in Excel: prefix them with a quote.
$safe = static fn(string $s): string => preg_match('/^[=+\-@]/', $s) ? "'" . $s : $s;
fputcsv($fh, [
    gmdate('Y-m-d H:i:s'), $safe($name), $safe($phone), $product, implode(' ', $interests),
    'yes', $safe($page), $safe(mb_substr((string)($_SERVER['HTTP_USER_AGENT'] ?? ''), 0, 160)),
]);
flock($fh, LOCK_UN);
fclose($fh);

// Forward to the n8n workflow (Telegram alert), when the deploy configured one. The lead is
// already saved, so a slow or failing webhook never loses it.
$cfgFile = __DIR__ . '/sgps-config.php';
$cfg = is_file($cfgFile) ? include $cfgFile : [];
$hook = is_array($cfg) ? (string)($cfg['lead_webhook'] ?? '') : '';
if ($hook !== '' && function_exists('curl_init')) {
    $LABELS = [
        'graphic-design-101' => 'Graphic Design 101', 'advertising-mastery' => 'Advertising Mastery',
        'ai-101' => 'AI & Automation 101', 'ai-mastery' => 'AI & Automation Mastery',
        'ai-100x-creatives' => 'AI 100x Creatives', 'not-sure' => 'محتاج مساعدة يختار',
    ];
    // WhatsApp link: Egyptian local numbers (01xxxxxxxxx) become 201xxxxxxxxx.
    $wa = (strlen($digits) === 11 && str_starts_with($digits, '01')) ? '2' . $digits : $digits;
    $payload = json_encode([
        'time_utc' => gmdate('Y-m-d H:i:s'),
        'name' => $name,
        'phone' => $phone,
        'whatsapp' => 'https://wa.me/' . $wa,
        'product' => $product,
        'interests' => array_map(static fn($i) => $LABELS[$i] ?? $i, $interests),
        'page' => $page,
    ], JSON_UNESCAPED_UNICODE);
    $ch = curl_init($hook);
    curl_setopt_array($ch, [
        CURLOPT_POST => true,
        CURLOPT_POSTFIELDS => $payload,
        CURLOPT_HTTPHEADER => ['Content-Type: application/json'],
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_CONNECTTIMEOUT => 3,
        CURLOPT_TIMEOUT => 5,
    ]);
    curl_exec($ch);
    curl_close($ch);
}

reply(200, ['ok' => true]);
