<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Dashboard - PixeTopup</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&family=Bebas+Neue&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #E8272A;
            --accent: #FF8C00;
            --surface: #FFFFFF;
            --surface-alt: #F4F5F7;
            --sidebar-bg: #1A1A2E;
            --border: #E8EAED;
            --text-main: #1A1A2E;
            --text-secondary: #6B7280;
            --text-muted: #9CA3AF;
            --green: #16A34A;
            --green-bg: #F0FDF4;
            --yellow: #D97706;
            --yellow-bg: #FFFBEB;
            --red: #DC2626;
            --red-bg: #FEF2F2;
            --shadow-sm: 0 1px 4px rgba(0,0,0,0.06);
            --shadow-md: 0 4px 16px rgba(0,0,0,0.08);
        }

        * { box-sizing: border-box; }
        body {
            background: var(--surface-alt);
            font-family: 'Nunito', sans-serif;
            color: var(--text-main);
            margin: 0;
        }

        /* ===== LAYOUT ===== */
        .admin-layout {
            display: flex;
            min-height: 100vh;
        }

        /* ===== SIDEBAR ===== */
        .sidebar {
            width: 240px;
            background: var(--sidebar-bg);
            flex-shrink: 0;
            display: flex;
            flex-direction: column;
            position: sticky;
            top: 0;
            height: 100vh;
            overflow-y: auto;
        }
        .sidebar-brand {
            padding: 24px 20px 20px;
            border-bottom: 1px solid rgba(255,255,255,0.07);
        }
        .sidebar-brand-name {
            font-family: 'Bebas Neue', sans-serif;
            font-size: 1.5rem;
            letter-spacing: 1.5px;
            color: #fff;
            display: block;
        }
        .sidebar-brand-name span { color: var(--primary); }
        .sidebar-brand-sub {
            font-size: 0.7rem;
            font-weight: 700;
            color: rgba(255,255,255,0.35);
            text-transform: uppercase;
            letter-spacing: 1px;
            display: block;
            margin-top: 2px;
        }
        .sidebar-nav {
            padding: 20px 12px;
            flex: 1;
        }
        .sidebar-section-label {
            font-size: 0.65rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 1.2px;
            color: rgba(255,255,255,0.25);
            padding: 0 8px;
            margin-bottom: 8px;
        }
        .sidebar-link {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px 12px;
            border-radius: 9px;
            color: rgba(255,255,255,0.6);
            text-decoration: none;
            font-size: 0.87rem;
            font-weight: 700;
            margin-bottom: 3px;
            transition: all 0.2s;
        }
        .sidebar-link:hover { background: rgba(255,255,255,0.07); color: rgba(255,255,255,0.9); }
        .sidebar-link.active { background: rgba(232,39,42,0.18); color: #ff7b7d; }
        .sidebar-link-icon { font-size: 1rem; width: 20px; text-align: center; flex-shrink: 0; }
        .sidebar-footer {
            padding: 16px 20px;
            border-top: 1px solid rgba(255,255,255,0.07);
        }
        .sidebar-footer a {
            display: flex;
            align-items: center; gap: 8px;
            color: rgba(255,255,255,0.4); text-decoration: none;
            font-size: 0.8rem; font-weight: 700;
            transition: color 0.2s;
        }
        .sidebar-footer a:hover { color: rgba(255,255,255,0.7); }

        /* ===== MAIN CONTENT ===== */
        .admin-main {
            flex: 1;
            min-width: 0;
            display: flex;
            flex-direction: column;
        }

        /* ===== TOP BAR ===== */
        .top-bar {
            background: var(--surface);
            border-bottom: 1px solid var(--border);
            padding: 0 28px;
            height: 64px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            position: sticky;
            top: 0;
            z-index: 50;
            box-shadow: var(--shadow-sm);
        }
        .page-title {
            font-size: 1.05rem;
            font-weight: 800;
            margin: 0;
            color: var(--text-main);
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .topbar-right {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .sync-btn {
            display: flex;
            align-items: center; gap: 6px;
            background: var(--primary);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 8px 16px;
            font-family: 'Nunito', sans-serif;
            font-size: 0.8rem;
            font-weight: 800;
            cursor: pointer;
            text-decoration: none;
            transition: all 0.2s;
        }
        .sync-btn:hover { background: var(--primary-dark); color: white; }

        /* ===== PAGE BODY ===== */
        .page-body {
            padding: 28px;
            flex: 1;
        }

        /* ===== STAT CARDS ===== */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 18px;
            margin-bottom: 28px;
        }
        .stat-card {
            background: var(--surface);
            border-radius: 14px;
            padding: 20px 22px;
            border: 1px solid var(--border);
            box-shadow: var(--shadow-sm);
            position: relative;
            overflow: hidden;
        }
        .stat-card::before {
            content: '';
            position: absolute;
            top: 0; right: 0;
            width: 60px; height: 60px;
            border-radius: 0 14px 0 60px;
            opacity: 0.08;
        }
        .stat-card.primary::before { background: var(--primary); }
        .stat-card.green::before { background: var(--green); }
        .stat-card.yellow::before { background: var(--yellow); }
        .stat-card.blue::before { background: #2563EB; }
        .stat-icon {
            width: 40px;
            height: 40px;
            border-radius: 10px;
            display: flex; align-items: center; justify-content: center;
            font-size: 1.1rem;
            margin-bottom: 14px;
        }
        .primary .stat-icon { background: #FEE2E2; color: var(--primary); }
        .green .stat-icon { background: var(--green-bg); color: var(--green); }
        .yellow .stat-icon { background: var(--yellow-bg); color: var(--yellow); }
        .blue .stat-icon { background: #EFF6FF; color: #2563EB; }
        .stat-label {
            font-size: 0.72rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            color: var(--text-muted);
            margin-bottom: 5px;
        }
        .stat-value {
            font-family: 'Bebas Neue', sans-serif;
            font-size: 2rem;
            line-height: 1;
            letter-spacing: 0.5px;
            color: var(--text-main);
        }
        .stat-unit {
            font-family: 'Nunito', sans-serif;
            font-size: 0.75rem;
            font-weight: 600;
            color: var(--text-muted);
            margin-top: 4px;
        }

        /* ===== TABLE ===== */
        .table-card {
            background: var(--surface);
            border-radius: 14px;
            border: 1px solid var(--border);
            box-shadow: var(--shadow-sm);
            overflow: hidden;
        }
        .table-card-header {
            padding: 18px 22px;
            border-bottom: 1px solid var(--border);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .table-card-title {
            font-size: 0.95rem;
            font-weight: 800;
            margin: 0;
        }
        .table-count {
            font-size: 0.75rem;
            font-weight: 700;
            color: var(--text-muted);
            background: var(--border);
            padding: 3px 10px;
            border-radius: 100px;
        }
        .trx-table {
            width: 100%;
            border-collapse: collapse;
        }
        .trx-table th {
            background: #FAFBFC;
            font-size: 0.71rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.7px;
            color: var(--text-muted);
            padding: 12px 18px;
            text-align: left;
            border-bottom: 1px solid var(--border);
        }
        .trx-table td {
            padding: 14px 18px;
            font-size: 0.86rem;
            font-weight: 600;
            color: var(--text-secondary);
            border-bottom: 1px solid var(--border);
            vertical-align: middle;
        }
        .trx-table tr:last-child td { border-bottom: none; }
        .trx-table tr:hover td { background: #FAFBFC; }
        .trx-table td strong { color: var(--text-main); font-weight: 800; font-size: 0.82rem; font-family: 'Bebas Neue', sans-serif; letter-spacing: 0.5px; }
        .trx-table td .date-text { font-size: 0.8rem; }
        .trx-table td .price-text { font-weight: 800; color: var(--text-main); }

        .status-pill {
            display: inline-flex;
            align-items: center;
            gap: 5px;
            font-size: 0.73rem;
            font-weight: 800;
            padding: 4px 11px;
            border-radius: 100px;
        }
        .status-pill.success { background: var(--green-bg); color: var(--green); }
        .status-pill.pending { background: var(--yellow-bg); color: var(--yellow); }
        .status-pill.failed  { background: var(--red-bg); color: var(--red); }
        .status-pill.manual  { background: #FECACA; color: #991B1B; border: 1px solid #F87171; }
        
        .status-pill::before { content: ''; display: inline-block; width: 6px; height: 6px; border-radius: 50%; background-color: currentColor; }

        .empty-row td {
            text-align: center;
            padding: 48px !important;
            color: var(--text-muted);
            font-size: 0.9rem;
        }
        .empty-row-icon { font-size: 2rem; display: block; margin-bottom: 8px; color: #cbd5e1; }

        /* ===== RESPONSIVE ===== */
        @media (max-width: 768px) {
            .sidebar { display: none; }
            .page-body { padding: 18px; }
            .stats-grid { grid-template-columns: repeat(2, 1fr); }
            .trx-table .hide-mobile { display: none; }
        }
    </style>
</head>
<body>

<div class="admin-layout">

    <aside class="sidebar">
        <div class="sidebar-brand">
            <span class="sidebar-brand-name">PIXIE<span>TOPUP</span></span>
            <span class="sidebar-brand-sub">Admin Panel</span>
        </div>
        <nav class="sidebar-nav">
            <div class="sidebar-section-label" style="margin-top:20px">Lainnya</div>
            <a href="/cek-pesanan" class="sidebar-link">
                <span class="sidebar-link-icon"><i class="fa-solid fa-magnifying-glass"></i></span>
                Cek Pesanan
            </a>
            
            <a href="/logout" class="sidebar-link" style="color: #FCA5A5; margin-top: 15px;">
                <span class="sidebar-link-icon"><i class="fa-solid fa-right-from-bracket"></i></span>
                Logout Sistem
            </a>
        </nav>
        <div class="sidebar-footer">
            <a href="/">
                <span><i class="fa-solid fa-globe"></i></span>
                <span>Lihat Website</span>
            </a>
        </div>
    </aside>

    <div class="admin-main">

        <div class="top-bar">
            <h1 class="page-title"><i class="fa-solid fa-chart-line" style="color: var(--text-muted);"></i> Dashboard Transaksi</h1>
            <div class="topbar-right">
                <a href="/admin-rahasia/cleanup" class="sync-btn" style="background-color: #6B7280;"><i class="fa-solid fa-broom"></i> Bersihkan Pending</a>
                <a href="/api/sync-products" class="sync-btn"><i class="fa-solid fa-rotate"></i> Sync Semua</a>
            </div>
        </div>

        <div class="page-body">

            <div class="stats-grid">
                <div class="stat-card primary">
                    <div class="stat-icon"><i class="fa-solid fa-box-open"></i></div>
                    <div class="stat-label">Total Transaksi</div>
                    <div class="stat-value">{{ total_trx }}</div>
                    <div class="stat-unit">pesanan masuk</div>
                </div>
                <div class="stat-card green">
                    <div class="stat-icon"><i class="fa-solid fa-wallet"></i></div>
                    <div class="stat-label">Estimasi Pendapatan</div>
                    <div class="stat-value" style="font-size:1.3rem">Rp {{ total_income | int | format_number }}</div>
                    <div class="stat-unit">dari transaksi sukses</div>
                </div>
                <div class="stat-card yellow">
                    <div class="stat-icon"><i class="fa-solid fa-circle-check"></i></div>
                    <div class="stat-label">Transaksi Sukses</div>
                    <div class="stat-value">{{ transactions | selectattr('status', 'in', ['SUCCESS', 'PAID', 'MANUAL']) | list | length }}</div>
                    <div class="stat-unit">uang berhasil masuk</div>
                </div>
                <div class="stat-card blue">
                    <div class="stat-icon"><i class="fa-solid fa-hourglass-half"></i></div>
                    <div class="stat-label">Masih Pending</div>
                    <div class="stat-value">{{ transactions | selectattr('status', 'equalto', 'PENDING') | list | length }}</div>
                    <div class="stat-unit">menunggu bayar</div>
                </div>
                
                <div class="stat-card" style="grid-column: 1 / -1; border-color: var(--primary);">
                    <div class="stat-label" style="color: var(--primary);">✨ Tambah Produk / Game Baru</div>
                    <form action="/admin-rahasia/tambah-game" method="POST" style="display: flex; gap: 10px; margin-top: 10px; align-items: stretch;">
                        <input type="text" name="nama_game" placeholder="Ketik nama game atau brand (Contoh: GENSHIN IMPACT, PLN, CALL OF DUTY)" required style="flex: 1; padding: 10px 15px; border-radius: 8px; border: 1.5px solid var(--border); font-family: 'Nunito', sans-serif; font-weight: 600; outline: none;">
                        <button type="submit" class="sync-btn" style="border-radius: 8px; height: 100%;"><i class="fa-solid fa-cloud-arrow-down"></i> Tarik Data</button>
                    </form>
                    <div class="stat-unit" style="margin-top: 8px;">Ketik nama brand sesuai dengan yang terdaftar di sistem Digiflazz.</div>
                </div>
            </div>

            <div class="table-card">
                <div class="table-card-header">
                    <h2 class="table-card-title">Riwayat Pesanan</h2>
                    <span class="table-count">{{ total_trx }} transaksi</span>
                </div>
                <div style="overflow-x: auto;">
                    <table class="trx-table">
                        <thead>
                            <tr>
                                <th>Tanggal</th>
                                <th>Order ID</th>
                                <th class="hide-mobile">ID Game</th>
                                <th class="hide-mobile">Item</th>
                                <th>Harga</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for trx in transactions %}
                            <tr>
                                <td><span class="date-text">{{ trx.created_at.strftime('%d/%m/%y %H:%M') }}</span></td>
                                <td><strong>{{ trx.order_id }}</strong></td>
                                <td class="hide-mobile">{{ trx.target_id }}</td>
                                <td class="hide-mobile" style="max-width:180px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{{ trx.product.item_name }}</td>
                                <td><span class="price-text">Rp {{ trx.sell_price | int | format_number }}</span></td>
                                <td>
                                    {% if trx.status == 'SUCCESS' or trx.status == 'PAID' %}
                                        <span class="status-pill success">Berhasil</span>
                                    {% elif trx.status == 'PENDING' %}
                                        <span class="status-pill pending">Pending</span>
                                    {% elif trx.status == 'MANUAL' %}
                                        <span class="status-pill manual">Perlu Manual</span>
                                        <div style="font-size: 0.75rem; color: #DC2626; margin-top: 6px; font-weight: 700;">
                                            Info: {{ trx.provider_log.get('data', {}).get('message', 'Error tidak terbaca') if trx.provider_log else 'Tidak ada log' }}
                                        </div>
                                    {% else %}
                                        <span class="status-pill failed">Gagal</span>
                                    {% endif %}
                                </td>
                            </tr>
                            {% else %}
                            <tr class="empty-row">
                                <td colspan="6">
                                    <span class="empty-row-icon"><i class="fa-regular fa-folder-open"></i></span>
                                    Belum ada transaksi sama sekali.
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>

        </div>
    </div>
</div>

</body>
</html>
