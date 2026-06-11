from flask import Blueprint, jsonify, request, render_template, session, redirect, url_for
from .models import Product, Transaction
from . import db
from .utils.digiflazz import cek_saldo, cek_harga, proses_topup 
from .utils.api_duitku import create_invoice
from datetime import datetime, timedelta
from .utils.security import limit_requests, verify_duitku_ip, login_required, verify_digiflazz_webhook

import uuid
import hashlib
import os
import re  # Ditambahkan untuk mengekstrak angka dari nama produk

main = Blueprint('main', __name__)

def otomatis_hapus_kadaluarsa():
    batas_waktu = datetime.utcnow() - timedelta(minutes=60)
    
    transaksi_lama = Transaction.query.filter(
        Transaction.status == 'PENDING',
        Transaction.created_at < batas_waktu
    ).all()
    
    if transaksi_lama:
        for trx in transaksi_lama:
            db.session.delete(trx)
        db.session.commit()

@main.route('/')
def home():
    try:
        otomatis_hapus_kadaluarsa()
    except Exception as e:
        pass 

    unique_games = db.session.query(Product.game_name).distinct().all()
    all_items = [game[0] for game in unique_games if game[0]] 
    
    kategori = {
        "Pilihan Game": [],
        "Pulsa dan Paket Data": [],
        "Token Listrik": [] 
    }
    
    pulsa_keywords = ["TELKOMSEL", "INDOSAT", "AXIS", "SMARTFREN", "TRI", "XL", "BY.U"]
    listrik_keywords = ["PLN", "TOKEN"]
    
    for item in all_items:
        item_upper = item.upper()
        
        if any(keyword in item_upper for keyword in pulsa_keywords):
            kategori["Pulsa dan Paket Data"].append(item)
        elif any(keyword in item_upper for keyword in listrik_keywords):
            kategori["Token Listrik"].append(item)
        else:
            kategori["Pilihan Game"].append(item)

    return render_template('index.html', kategori=kategori)

@main.route('/game/<slug>')
def game_detail(slug):
    game_name_clean = slug.replace('-', ' ')
    
    all_products = Product.query.filter(
        Product.game_name.ilike(f"%{game_name_clean}%"),
        Product.is_active == True
    ).order_by(Product.price.asc()).all()
    
    unique_products = {}
    for p in all_products:
        if p.item_name not in unique_products:
            unique_products[p.item_name] = p
            
    # ==========================================
    # LOGIKA HARGA DINAMIS (HANYA UNTUK TAMPILAN)
    # ==========================================
    game_upper = game_name_clean.upper()
    is_pulsa = any(k in game_upper for k in ["TELKOMSEL", "INDOSAT", "AXIS", "SMARTFREN", "TRI", "XL", "BY.U"])
    is_listrik = any(k in game_upper for k in ["PLN", "TOKEN"])
    
    final_products = []
    for p in unique_products.values():
        harga_tampil = p.price # Default pakai harga modal dari database
        
        if is_pulsa:
            nama_lower = p.item_name.lower()
            is_paket_data = any(k in nama_lower for k in ['data', 'internet', 'gb', 'hari', 'freedom', 'kuota', 'combo'])
            
            if not is_paket_data:
                # Ekstrak nominal pulsa
                angka_list = re.findall(r'\d+', p.item_name.replace('.', ''))
                if angka_list:
                    nominal = max([int(x) for x in angka_list])
                    if nominal >= 1000:
                        harga_tampil = nominal + 1000
        
        # --- LOGIKA HARGA KHUSUS PLN (+2000) ---
        elif is_listrik:
            angka_list = re.findall(r'\d+', p.item_name.replace('.', ''))
            if angka_list:
                nominal = max([int(x) for x in angka_list])
                if nominal >= 1000:
                    harga_tampil = nominal + 2000
        
        # Simpan ke variabel dinamis agar bisa dibaca di HTML (Tidak masuk/merubah Database)
        p.harga_jual_dinamis = harga_tampil
        final_products.append(p)
    # ==========================================
            
    display_name = game_name_clean.title()
    
    return render_template('game.html', game_name=display_name, products=final_products)

@main.route('/api/saldo', methods=['GET'])
def get_saldo():
    hasil = cek_saldo()
    return jsonify(hasil)

@main.route('/api/sync-products', methods=['GET'])
def sync_products():
    unique_games = db.session.query(Product.game_name).distinct().all()
    target_games_db = [game[0].upper() for game in unique_games if game[0]]
    
    target_games_default = ["MOBILE LEGENDS", "FREE FIRE", "PUBG MOBILE", "TELKOMSEL", "INDOSAT"]
    target_games = list(set(target_games_default + target_games_db))
    
    total_synced = 0
    hasil = cek_harga("") 
    
    if hasil.get("status") == "success":
        data_digiflazz = hasil.get("data", [])
        
        if isinstance(data_digiflazz, dict) and "message" in data_digiflazz:
            return jsonify({"status": "error", "message": f"Ditolak Digiflazz: {data_digiflazz.get('message')}"})
            
        Product.query.update({Product.is_active: False})

        for item in data_digiflazz:
            brand_produk = str(item.get("brand", "")).upper()
            
            game_terdeteksi = None
            for target in target_games:
                if target in brand_produk:
                    game_terdeteksi = target
                    break
            
            if game_terdeteksi:
                sku = item.get("buyer_sku_code")
                existing_product = Product.query.filter_by(provider_code=sku).first()
                
                # --- KEMBALI SIMPAN HARGA MODAL ASLI KE DATABASE ---
                harga_modal = item.get("price", 0)
                status_aktif = item.get("buyer_product_status", True) and item.get("seller_product_status", True)
                
                if existing_product:
                    existing_product.price = harga_modal
                    existing_product.is_active = status_aktif
                else:
                    new_product = Product(
                        game_name=game_terdeteksi,
                        item_name=item.get("product_name"),
                        provider_code=sku,
                        price=harga_modal,
                        is_active=status_aktif
                    )
                    db.session.add(new_product)
                
                total_synced += 1

    try:
        db.session.commit()
        return jsonify({"status": "success", "message": f"Berhasil sinkronisasi {total_synced} produk ke database!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": f"Gagal menyimpan data ke database: {str(e)}"})

@main.route('/api/products', methods=['GET'])
def get_products():
    products = Product.query.filter_by(is_active=True).all()
    katalog = []
    for p in products:
        katalog.append({
            "id": p.id,
            "game_name": p.game_name,
            "item_name": p.item_name,
            "harga_jual": p.price,
            "sku": p.provider_code
        })
    return jsonify({"status": "success", "total_produk": len(katalog), "data": katalog})

@main.route('/api/checkout', methods=['POST'])
@limit_requests(max_requests=5, window=60) 
def checkout():
    data = request.json
    product_id = data.get('product_id')
    target_id = data.get('target_id')
    payment_method = data.get('payment_method') 
    
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"status": "error", "message": "Produk tidak ditemukan"})
        
    # ==========================================
    # LOGIKA HARGA DINAMIS (KEUNTUNGAN + ADMIN)
    # ==========================================
    game_upper = product.game_name.upper()
    is_pulsa = any(k in game_upper for k in ["TELKOMSEL", "INDOSAT", "AXIS", "SMARTFREN", "TRI", "XL", "BY.U"])
    is_listrik = any(k in game_upper for k in ["PLN", "TOKEN"])
    is_game = not (is_pulsa or is_listrik)
    
    final_price = product.price # Base price dari database murni modal Digiflazz
    is_paket_data = False
    
    # --- LOGIKA HARGA KHUSUS PULSA (+ 1000 SAAT BAYAR UNTUK PULSA BIASA) ---
    if is_pulsa:
        nama_lower = product.item_name.lower()
        is_paket_data = any(k in nama_lower for k in ['data', 'internet', 'gb', 'hari', 'freedom', 'kuota', 'combo'])
        if not is_paket_data:
            angka_list = re.findall(r'\d+', product.item_name.replace('.', ''))
            if angka_list:
                nominal = max([int(x) for x in angka_list])
                if nominal >= 1000:
                    final_price = nominal + 1000
                    
    # --- LOGIKA HARGA KHUSUS PLN (+ 2000) ---
    elif is_listrik:
        angka_list = re.findall(r'\d+', product.item_name.replace('.', ''))
        if angka_list:
            nominal = max([int(x) for x in angka_list])
            if nominal >= 1000:
                final_price = nominal + 2000
    # -----------------------------------------------------

    # --- LOGIKA KEUNTUNGAN PERSENTASE (HANYA GAME & PAKET DATA) ---
    kena_margin_persen = is_game or is_paket_data

    if kena_margin_persen:
        if payment_method == 'NQ': # QRIS / GoPay
            final_price = final_price + (final_price * 0.107)
        elif payment_method in ['OV', 'DA', 'LA']: # OVO, DANA, LinkAja
            final_price = final_price + (final_price * 0.1167)
        elif payment_method == 'SP': # ShopeePay
            final_price = final_price + (final_price * 0.12)
        elif payment_method in ['BC', 'M2', 'BR', 'I1']: # Virtual Account Bank (10% + 4000)
            final_price = final_price + (final_price * 0.10) + 4000
        else: # Metode lain seperti minimarket
            final_price = final_price + (final_price * 0.10) + 2500
            
    final_price = int(final_price) # Membulatkan ke angka genap terdekat
    # ==========================================

    order_id = f"PX-{uuid.uuid4().hex[:8].upper()}"
    
    duitku_res = create_invoice(
        order_id=order_id, 
        amount=final_price, 
        payment_method=payment_method, 
        product_details=product.item_name
    )
    
    if duitku_res.get('statusCode') == '00':
        new_trx = Transaction(
            order_id=order_id,
            target_id=target_id,
            product_id=product.id,
            sell_price=final_price,
            provider_price=product.price, # HARGA MODAL ASLI DIGIFLAZZ AMAN DI SINI!
            customer_phone="08123456789", 
            payment_method=payment_method,
            status='PENDING'
        )
        db.session.add(new_trx)
        db.session.commit()
        
        return jsonify({
            "status": "success",
            "message": "Pesanan berhasil dibuat!",
            "order_id": order_id,
            "payment_url": duitku_res.get('paymentUrl') 
        })
    else:
        return jsonify({
            "status": "error",
            "message": "Gagal menghubungi sistem pembayaran",
            "detail": duitku_res
        })

@main.route('/api/callback/duitku', methods=['POST'])
@verify_duitku_ip 
def callback_duitku():
    data = request.form if request.form else request.json
    if not data:
        return jsonify({"status": "error", "message": "Data kosong"}), 400
        
    merchant_code = data.get('merchantCode')
    amount = data.get('amount')
    order_id = data.get('merchantOrderId')
    signature = data.get('signature')
    result_code = data.get('resultCode') 
    
    api_key = os.getenv('DUITKU_API_KEY')
    
    sign_str = f"{merchant_code}{amount}{order_id}{api_key}"
    calc_sign = hashlib.md5(sign_str.encode()).hexdigest()
    
    if calc_sign != signature:
        return jsonify({"status": "error", "message": "Signature tidak valid! Anda Hacker?"}), 403
        
    trx = Transaction.query.get(order_id)
    if not trx:
        return jsonify({"status": "error", "message": "Pesanan tidak ditemukan"}), 404
        
    if result_code == '00' and trx.status == 'PENDING':
        trx.status = 'PAID'
        db.session.commit()
        
        kode_sku = trx.product.provider_code
        
        topup_res = proses_topup(trx.target_id, kode_sku, trx.order_id)
        trx.provider_log = topup_res
        status_digiflazz = topup_res.get('data', {}).get('status')
        
        if status_digiflazz in ['Sukses', 'Pending']:
            trx.status = 'PROCESSING'
        else:
            trx.status = 'MANUAL' 
            
        db.session.commit()
        
    elif result_code == '01':
        trx.status = 'FAILED'
        db.session.commit()
    
    return jsonify({"status": "success"}), 200

@main.route('/api/callback/digiflazz', methods=['POST'])
@verify_digiflazz_webhook
def callback_digiflazz():
    data = request.json
    if not data or 'data' not in data:
        return jsonify({"status": "error", "message": "Data tidak valid"}), 400
        
    payload_data = data.get('data', {})
    ref_id = payload_data.get('ref_id') 
    status = payload_data.get('status')
    
    if not ref_id:
        return jsonify({"status": "error", "message": "ref_id tidak ditemukan"}), 400
        
    trx = Transaction.query.get(ref_id)
    if not trx:
        return jsonify({"status": "error", "message": "Transaksi tidak ditemukan"}), 404
        
    trx.provider_log = payload_data
    
    if status == 'Sukses':
        trx.status = 'SUCCESS'
    elif status == 'Gagal':
        trx.status = 'FAILED'
    
    db.session.commit()
    return jsonify({"status": "success"}), 200

@main.route('/api/cek-id', methods=['POST'])
def cek_id():
    import time
    
    data = request.json
    game_name = data.get('game_name')
    target_id = data.get('target_id')

    CHECKER_SKU = {
        "MOBILE LEGENDS": "pre31831538",
        "FREE FIRE": "pre31831544"
    }

    sku_checker = CHECKER_SKU.get(game_name.upper())

    if not sku_checker:
        return jsonify({"status": "skip", "message": "Game ini belum mendukung Cek ID otomatis."})

    ref_id = f"CEK-{uuid.uuid4().hex[:8].upper()}"
    
    hasil = proses_topup(target_id, sku_checker, ref_id)
    
    status_digi = hasil.get('data', {}).get('status')
    sn = hasil.get('data', {}).get('sn', '')
    pesan = hasil.get('data', {}).get('message', '')

    maksimal_tunggu = 4
    percobaan = 0

    while status_digi == 'Pending' and not sn and percobaan < maksimal_tunggu:
        time.sleep(2.5)
        
        hasil = proses_topup(target_id, sku_checker, ref_id) 
        
        status_digi = hasil.get('data', {}).get('status')
        sn = hasil.get('data', {}).get('sn', '')
        pesan = hasil.get('data', {}).get('message', '')
        
        percobaan += 1

    if status_digi in ['Sukses', 'Pending']:
        if sn:
            parts = [p.strip() for p in sn.split('/')]
            nickname_bersih = sn 
            
            for part in parts:
                if part.lower().startswith('username'):
                    nickname_bersih = part[8:].strip()
                    break
            else:
                if len(parts) >= 2:
                    nickname_bersih = parts[1]
                    
            nickname_ditemukan = nickname_bersih
            
        elif status_digi == 'Pending':
            nickname_ditemukan = "ID Valid (Nama disembunyikan provider)"
        else:
            nickname_ditemukan = pesan
            
        return jsonify({
            "status": "success", 
            "nickname": nickname_ditemukan
        })
    else:
        pesan_error_asli = hasil.get('data', {}).get('message', 'Terjadi kesalahan tidak diketahui.')
        return jsonify({
            "status": "error", 
            "message": f"Ditolak Digiflazz: {pesan_error_asli}"
        })

@main.route('/success')
def success_page():
    order_id = request.args.get('merchantOrderId')
    
    if not order_id:
        return "Order ID tidak ditemukan.", 400
        
    trx = Transaction.query.get(order_id)
    if not trx:
        return "Transaksi tidak ditemukan di sistem.", 404
        
    return render_template('success.html', order_id=trx.order_id, status=trx.status, trx=trx)

@main.route('/cek-pesanan', methods=['GET', 'POST'])
def cek_pesanan():
    trx = None
    error_msg = None
    
    if request.method == 'POST':
        order_id_input = request.form.get('order_id')
        
        if order_id_input:
            trx = Transaction.query.get(order_id_input.strip())
            if not trx:
                error_msg = "Pesanan tidak ditemukan. Pastikan Nomor Invoice (Order ID) sudah benar."
                
    return render_template('cek_pesanan.html', trx=trx, error_msg=error_msg)

@main.route('/api/cek-status/<order_id>', methods=['GET'])
def cek_status_api(order_id):
    trx = Transaction.query.get(order_id)
    if not trx:
        return jsonify({"status": "error", "message": "Not found"}), 404

    return jsonify({
        "status": "success",
        "trx_status": trx.status
    })

@main.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('admin_logged_in'):
        return redirect(url_for('main.admin_dashboard'))
        
    error_msg = None
    if request.method == 'POST':
        username_input = request.form.get('username')
        password_input = request.form.get('password')
        
        admin_user = os.getenv('ADMIN_USERNAME', 'admin')
        admin_pass = os.getenv('ADMIN_PASSWORD', 'admin123')
        
        if username_input == admin_user and password_input == admin_pass:
            session['admin_logged_in'] = True
            return redirect(url_for('main.admin_dashboard'))
        else:
            error_msg = "Username atau password salah!"
            
    return render_template('login.html', error_msg=error_msg)

@main.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('main.login'))

@main.route('/admin-rahasia/tambah-game', methods=['POST'])
@login_required
def tambah_game_baru():
    nama_game = request.form.get('nama_game')
    if not nama_game:
        return "Nama game kosong", 400
        
    nama_game_upper = nama_game.upper().strip()
    hasil = cek_harga("") 
    total_added = 0
    
    if hasil.get("status") == "success":
        data_digiflazz = hasil.get("data", [])
        
        if isinstance(data_digiflazz, dict) and "message" in data_digiflazz:
            pesan_error = data_digiflazz.get('message')
            return f"<script>alert('Gagal! Digiflazz menolak akses. Alasan: {pesan_error}'); window.location.href='/admin-rahasia';</script>"

        for item in data_digiflazz:
            brand_produk = str(item.get("brand", "")).upper()
            
            if nama_game_upper in brand_produk:
                sku = item.get("buyer_sku_code")
                existing_product = Product.query.filter_by(provider_code=sku).first()
                
                # --- KEMBALI SIMPAN HARGA MODAL ASLI KE DATABASE ---
                harga_modal = item.get("price", 0)
                status_aktif = item.get("buyer_product_status", True) and item.get("seller_product_status", True)
                
                if existing_product:
                    existing_product.price = harga_modal
                    existing_product.is_active = status_aktif
                else:
                    new_product = Product(
                        game_name=nama_game_upper,
                        item_name=item.get("product_name"),
                        provider_code=sku,
                        price=harga_modal,
                        is_active=status_aktif
                    )
                    db.session.add(new_product)
                
                total_added += 1
        
        if total_added > 0:
            db.session.commit()
            return f"<script>alert('Sukses! {total_added} produk {nama_game_upper} berhasil ditambahkan ke database.'); window.location.href='/admin-rahasia';</script>"
        else:
            return f"<script>alert('Gagal: Produk dengan nama {nama_game_upper} tidak ditemukan di Digiflazz.'); window.location.href='/admin-rahasia';</script>"
            
    return f"Gagal terhubung ke Digiflazz. Pesan asli: {hasil}"

@main.route('/admin-rahasia')
@login_required
def admin_dashboard():
    try:
        otomatis_hapus_kadaluarsa()
    except Exception as e:
        pass 

    transactions = Transaction.query.order_by(Transaction.created_at.desc()).all()
    total_trx = len(transactions)
    
    total_income = sum(trx.sell_price for trx in transactions if trx.status in ['PAID', 'SUCCESS', 'MANUAL', 'PROCESSING'])
    
    return render_template('admin.html', transactions=transactions, total_trx=total_trx, total_income=total_income)

@main.route('/admin-rahasia/cleanup')
@login_required
def cleanup_pending():
    batas_waktu = datetime.utcnow() - timedelta(hours=24)
    
    transaksi_kedaluwarsa = Transaction.query.filter(
        Transaction.status == 'PENDING',
        Transaction.created_at < batas_waktu
    ).all()
    
    jumlah_dihapus = len(transaksi_kedaluwarsa)
    
    for trx in transaksi_kedaluwarsa:
        db.session.delete(trx)
        
    db.session.commit()
    
    return f"Berhasil menghapus {jumlah_dihapus} transaksi PENDING yang sudah kedaluwarsa! <br><br> <a href='/admin-rahasia'>Kembali ke Dashboard</a>"
