from database.models import User, Appointment, async_session
from sqlalchemy import ScalarResult, select


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


