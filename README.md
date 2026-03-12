# BookStore Microservices

Assignment 05 & 06 — 12 microservices (Django REST), PostgreSQL/MySQL, API Gateway with role-based login.

## Quick start

```bash
docker-compose up --build
```

Open **http://localhost:8000** (API Gateway). Guest can browse books only; login or register for cart and orders.

---

## Demo accounts (password: `pass`)

**Đăng nhập:** chỉ cần nhập email + mật khẩu. Hệ thống tự xác định vai trò theo DB (thử manager → staff → customer). Không cần chọn role.

### Customer (mua sách, giỏ hàng, đơn hàng)

| Email              | Password | Ghi chú   |
|--------------------|----------|-----------|
| alice@example.com  | pass     | Customer  |
| bob@example.com    | pass     | Customer  |
| charlie@example.com| pass     | Customer  |

- **Đăng ký:** chỉ dành cho khách hàng — dùng link **Đăng ký** trên trang Login (hoặc nav) để tạo tài khoản customer. Staff/Shipper/Manager do manager tạo.
- Sau khi đăng nhập: xem sách, thêm giỏ, đặt hàng, xem đơn, thanh toán.

### Staff — nhân viên bán hàng (quản lý sách)

| Email           | Password | Role  | Ghi chú        |
|-----------------|----------|-------|----------------|
| staff@store.com | pass     | staff | Quản lý sách   |
| admin@store.com | pass     | staff | Quản lý sách   |

- Đăng nhập bằng email staff → vào **Manage Books** (thêm/sửa/xóa sách).

### Shipper (nhân viên giao hàng)

| Email             | Password | Role    | Ghi chú              |
|-------------------|----------|---------|----------------------|
| shipper1@store.com| pass     | shipper | Nhận đơn, xem đơn của mình |
| shipper2@store.com| pass     | shipper | Nhận đơn, xem đơn của mình |

- Đăng nhập bằng email shipper → hệ thống nhận diện **shipper** và chuyển vào **My Deliveries**.
- **Đơn chưa giao cho ai:** danh sách đơn đã confirm nhưng chưa có shipper → bấm **Nhận đơn** để nhận giao.
- **Đơn của tôi:** danh sách đơn đã được giao cho bạn.

### Manager (quản lý)

| Email            | Password | Ghi chú              |
|------------------|----------|------------------------|
| manager@store.com| pass     | Quản lý orders, users, payments |
| admin@store.com  | pass     | Manager (cùng email có thể dùng staff) |

- Đăng nhập bằng email manager → Orders (hủy đơn, gán shipper), **Users** (xem danh sách + **tạo tài khoản mới** với vai trò Customer / Staff / Shipper), Payments (lịch sử thanh toán).

---

## Phân quyền tóm tắt

| Role     | Sau khi đăng nhập        | Tính năng chính |
|----------|---------------------------|-----------------|
| Guest    | Chỉ xem danh sách sách   | Không cart, không đơn |
| Customer | Books, Cart, Orders       | Mua sách, đặt hàng, thanh toán, xem đơn & trạng thái ship |
| Staff    | Store + Manage Books      | CRUD sách       |
| Shipper  | Store + My Deliveries     | Xem đơn chưa giao, nhận đơn, xem đơn của mình |
| Manager  | Orders, Users, Payments   | Hủy đơn, gán shipper, **tạo tài khoản** (customer/staff/shipper), lịch sử thanh toán |

---

## Services & ports

| Service              | Port | DB        |
|----------------------|------|-----------|
| api-gateway           | 8000 | —         |
| customer-service      | 8001 | PostgreSQL|
| book-service          | 8002 | MySQL     |
| cart-service          | 8003 | MySQL     |
| order-service         | 8004 | PostgreSQL|
| pay-service           | 8005 | PostgreSQL|
| ship-service          | 8006 | PostgreSQL|
| staff-service         | 8007 | PostgreSQL|
| manager-service       | 8008 | PostgreSQL|
| catalog-service       | 8009 | MySQL     |
| comment-rate-service  | 8010 | MySQL     |
| recommender-ai-service| 8011 | —         |

PostgreSQL: 5432, MySQL: 3306 (internal).

---

## Tech

- Django REST Framework, Docker Compose, PostgreSQL 15, MySQL 8.
- Gateway: session-based role (customer / staff / manager), staff sub-role (staff vs shipper).
