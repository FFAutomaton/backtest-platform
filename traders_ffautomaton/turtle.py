# import math
# import statistics
# import time
# import pandas as pd
# from data.schemas.enums.decision import Decision
# from data.schemas.enums.position import Position
# import pandas_ta as ta
# import math
#
#
# class TurtleTrader:
#
#     def __init__(self, logger):
#         self.atr_save = None
#         self.logger = logger
#         self.current_price = None
#         self.amount = None
#         # self.state = {
#         #     amount: self.amount,
#         # }
#         self.entryPrice = None
#         self.entry_stop_loss = None
#         self.atr_value = None
#         self.entry_amount = None
#
#         self.last_20_highest = None
#         self.last_20_lowest = None
#         self.last_10_highest = None
#         self.last_10_lowest = None
#
#         self.amount_from_config = None
#         self.current_position = Position.notr
#
#         self.active_stop_loss = 0
#         self.pyramid_count = 0
#         self.stop_losses = [None] * 4
#         self.pyramid_entries = [None] * 3
#         self.pyramid_stop_losses = [None] * 3
#
#     def reset_turtle(self):
#         self.current_position = Position.notr
#
#     def update_turtle_state(self, position):
#         self.current_position = position
#         if position != Position.notr:
#             self.active_stop_loss = self.stop_losses[self.pyramid_count]
#             self.logger.info(
#                 msg=f"update_turtle_state active sl: {self.active_stop_loss}, pyramid count {self.pyramid_count}")
#
#     def update_turtle_data(self, series):
#         self.calculate_atr(series)
#         self.update_turtle_high_and_low(series)
#         if self.current_position == Position.notr:
#             self.calculate_entry_amount()
#         self.logger.info(
#             msg=f"amount: {self.amount}, atr: {self.atr_value} atr_save: {self.atr_save}, 20-10 high low: {self.last_20_highest}, {self.last_20_lowest}, {self.last_10_highest}, {self.last_10_lowest}")
#
#     def update_turtle_high_and_low(self, data) -> None:
#         self.last_20_highest = max(data.high[-20:])
#         self.last_20_lowest = min(data.low[-20:])
#         self.last_10_highest = max(data.high[-10:])
#         self.last_10_lowest = min(data.low[-10:])
#
#     def calculate_atr(self, series, window=20) -> None:
#         series = series.sort_values(by="time", ascending=True)
#         indicator = ta.atr(high=series["high"], low=series["low"], close=series["close"], length=window, mamode="EMA")
#         values = indicator.tail(2).iloc[1]
#         self.atr_value = values
#         if self.current_position == Position.notr:
#             self.atr_save = values
#
#     def calculate_entry_amount(self) -> float:
#         self.amount = float(self.amount_from_config * (1 / (self.atr_value * 2)))
#         return self.amount
#
#     def calculate_stop_loss(self, decision, entry_price, atr_value) -> float:
#         temp_stop_loss_value = 0
#         if decision == Decision.buy:
#             temp_stop_loss_value = float(entry_price - (2 * atr_value))
#         elif decision == Decision.sell:
#             temp_stop_loss_value = float(entry_price + (2 * atr_value))
#         self.logger.info(msg=f"atr value is  {atr_value}, calculate_stop_loss: {temp_stop_loss_value}")
#         self.active_stop_loss = temp_stop_loss_value
#         return temp_stop_loss_value
#
#     def check_position_exit(self, position, current_price) -> Decision:
#         if position == Position.long:
#             cond_a = bool(current_price < self.last_10_lowest)
#             cond_b = bool(current_price < self.active_stop_loss)
#             self.logger.info(msg=f"check_position_exit: {cond_a}, {cond_b}")
#             if cond_a or cond_b:
#                 return Decision.market_exit
#         elif position == Position.short:
#             cond_a = bool(current_price > self.last_10_highest)
#             cond_b = bool(current_price > self.active_stop_loss)
#             self.logger.info(msg=f"check_position_exit: {cond_a}, {cond_b}")
#             if cond_a or cond_b:
#                 return Decision.market_exit
#         return Decision.do_nothing
#
#     def calculate_pyramid_entry_stop_values(self, decision, stop_loss, current_price) -> list:
#         if decision == Decision.buy:
#             pyramid_one_entry = current_price + (0.5 * self.atr_save)
#             pyramid_two_entry = current_price + (1.0 * self.atr_save)
#             pyramid_three_entry = current_price + (1.5 * self.atr_save)
#
#             pyramid_one_stop = stop_loss + (0.5 * self.atr_save)
#             pyramid_two_stop = stop_loss + (1.0 * self.atr_save)
#             pyramid_three_stop = stop_loss + (1.5 * self.atr_save)
#         else:
#             pyramid_one_entry = current_price - (0.5 * self.atr_save)
#             pyramid_two_entry = current_price - (1.0 * self.atr_save)
#             pyramid_three_entry = current_price - (1.5 * self.atr_save)
#
#             pyramid_one_stop = stop_loss - (0.5 * self.atr_save)
#             pyramid_two_stop = stop_loss - (1.0 * self.atr_save)
#             pyramid_three_stop = stop_loss - (1.5 * self.atr_save)
#         self.pyramid_entries[0] = pyramid_one_entry
#         self.pyramid_entries[1] = pyramid_two_entry
#         self.pyramid_entries[2] = pyramid_three_entry
#
#         self.pyramid_stop_losses[0] = pyramid_one_stop
#         self.pyramid_stop_losses[1] = pyramid_two_stop
#         self.pyramid_stop_losses[2] = pyramid_three_stop
#
#         out_array = [self.pyramid_entries, self.pyramid_stop_losses]
#         return out_array
#
#     def check_pyramid(self, position, current_price) -> Decision:
#         if self.pyramid_count >= 3:
#             return Decision.do_nothing
#         if position == Position.long:
#             if current_price >= self.pyramid_entries[self.pyramid_count]:
#                 self.logger.info(msg=f"pyramid activated {self.pyramid_count}")
#                 return Decision.pyramid
#         else:
#             if current_price <= self.pyramid_entries[self.pyramid_count]:
#                 self.logger.info(msg=f"pyramid activated {self.pyramid_count}")
#                 return Decision.pyramid
#         return Decision.do_nothing
#
#     def in_position_loop(self) -> Decision:
#         exit_condition = self.check_position_exit(self.current_position, self.current_price)
#         if exit_condition != Decision.do_nothing:
#             return Decision.market_exit
#         else:
#             pyramid_decision = self.check_pyramid(self.current_position, self.current_price)
#             if pyramid_decision == Decision.pyramid:
#                 return Decision.pyramid
#             else:
#                 return Decision.do_nothing
#
#     def not_in_position_loop(self) -> Decision:
#         decision = Decision.do_nothing
#         if self.current_price >= self.last_20_highest:
#             self.calculate_entry_amount()
#             self.logger.info(msg=f"long position opened at {self.current_price}")
#             decision = Decision.buy
#         elif self.current_price <= self.last_20_lowest:
#             self.calculate_entry_amount()
#             self.logger.info(msg=f"short position opened at {self.current_price}")
#             decision = Decision.sell
#         if decision != Decision.do_nothing:
#             self.entry_stop_loss = self.calculate_stop_loss(decision, self.current_price, self.atr_save)
#             pyramid_stoplosses = self.calculate_pyramid_entry_stop_values(decision, self.entry_stop_loss,
#                                                                           self.current_price)
#             self.stop_losses = [self.entry_stop_loss] + pyramid_stoplosses[1]
#         return decision
#
#
