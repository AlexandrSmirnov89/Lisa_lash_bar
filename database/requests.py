from database.models import User, Appointment, Image, async_session
from sqlalchemy import ScalarResult, select, delete


async def add_free_appointment(date, time):
    session = async_session()

    try:
        new_appointment = Appointment(date=date, time=time, status='Пустая запись')
        session.add(new_appointment)

        await session.commit()
    finally:
        await session.close()


async def get_appointment(date):
    async with async_session() as session:
        result = await session.scalars(select(Appointment).where(Appointment.date == date))
        return result


async def get_all_appointment():
    async with async_session() as session:
        result = await session.scalars(select(Appointment))
        return result
    
    
async def get_curr_user_appoint(tg_id):
    async with async_session() as session:
        result = await session.scalars(select(Appointment)
                                       .join(User, Appointment.user_id == User.id)
                                       .where(User.tg_id == tg_id)
                                       .where(Appointment.status == 'Подтверждено'))
        return result
    

async def get_category_photos():
    async with async_session() as session:
        result = await session.scalars(select(Image.category)
                                       .distinct())
                
        return result
    

async def add_photo(url_photo, category):
    async with async_session() as session:
        new_photo = Image(image_url=url_photo, category=category)
        
        session.add(new_photo)
        await session.commit()
        
        
async def get_photos(category):
    async with async_session() as session:
        result = await session.scalars(select(Image.image_url)
                                       .where(Image.category == category))
        
        return result
    

async def del_photo(url):
    async with async_session() as session:
        stmt = delete(Image).where(Image.image_url == url)
        await session.execute(stmt)
        await session.commit()
        

async def del_category(category):
    async with async_session() as session:
        stmt = delete(Image).where(Image.category == category)
        await session.execute(stmt)
        await session.commit()
        
        
async def del_appoint(appoint_id):
    async with async_session() as session:
        stmt = delete(Appointment).where(Appointment.id == int(appoint_id))
        await session.execute(stmt)
        await session.commit()
        
        
# async def change_of_status(appoint_id, status, user_data):
#     async with async_session() as session:
#         user = await session.get(User, user_data.id)
#         if user is None:
#             new_users = User(tg_id=user_data.id,
#                              first_name=user_data.first_name,
#                              last_name=user_data.last_name or 'не указано',
#                              phone_number='не указано')
#             session.add(new_users)
#             await session.commit()
#             user = new_users
#         else:
#             user.first_name = user_data.first_name
#             user.last_name = user_data.last_name or 'не указано'
#             user.phone_number = 'не указано'
#
#         appointment = await session.get(Appointment, int(appoint_id))
#
#         appointment.status = status
#         appointment.user_id = user.id
#
#         await session.commit()

async def change_of_status(appoint_id, status, user_data):
    async with async_session() as session:
        user: ScalarResult[User] = await session.scalars(select(User).where(User.tg_id == int(user_data.user_id)))
        
        result_user: User = user.first()
        
        
        if result_user is None:
            user = User(first_name=user_data.first_name,
                        last_name=user_data.last_name or 'не указано',
                        phone_number=user_data.phone_number,
                        tg_id=user_data.user_id)
            
            print("ВЫВОД   ->   :  ПОЛЬЗОВАТЕЛЯ НЕ БЫЛО В БАЗЕ")

            session.add(user)
            await session.commit()
            user: ScalarResult[User] = await session.scalars(select(User).where(User.tg_id == int(user_data.user_id)))
            result_user: User = user.first()

        print('ВЫВОД   ->   :  ', result_user.tg_id)

        appointment = await session.get(Appointment, int(appoint_id))
        print('ВЫВОД   ->   :  ', appointment.status)

        appointment.status = status
        appointment.user_id = result_user.id

        await session.commit()


